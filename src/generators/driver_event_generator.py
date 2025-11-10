"""Driver event batch generator with Poisson inter-arrival and weighted sampling."""

import argparse
import json
import signal
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np

from src.generators.base import BaseGenerator
from src.generators.config import Config
from src.generators.coordination import get_onboarded_companies_before
from src.generators.models import DriverEventBatch, DriverEventRecord, BatchManifest
from src.generators.injector import QualityInjector


class DriverEventGenerator(BaseGenerator):
    """
    Generator for 15-minute driver event batches.
    
    Implements:
    - Poisson inter-arrival for event counts per driver
    - Weighted categorical sampling for event_type
    - Interval boundary enforcement
    - Company coordination (only reference companies created before interval)
    """
    
    def __init__(self):
        """Initialize driver event generator."""
        super().__init__()
        self.shutdown_requested = False
    
    def compute_interval_bounds(self, now: datetime, interval_minutes: int = 15) -> Tuple[datetime, datetime]:
        """
        Compute interval boundaries aligned to interval_minutes multiples.
        
        Args:
            now: Current timestamp
            interval_minutes: Interval duration in minutes (default 15)
            
        Returns:
            Tuple of (interval_start, interval_end) where start is aligned to interval multiples
            
        Example:
            now=12:17 -> (12:15, 12:30) for 15-minute intervals
        """
        # Align to interval_minutes multiples
        aligned_minute = (now.minute // interval_minutes) * interval_minutes
        interval_start = now.replace(minute=aligned_minute, second=0, microsecond=0)
        interval_end = interval_start + timedelta(minutes=interval_minutes)
        
        return interval_start, interval_end
    
    def generate_driver_events(
        self,
        companies: List[str],
        config: Config,
        interval_start: datetime,
        interval_end: datetime,
        seed: int
    ) -> List[DriverEventRecord]:
        """
        Generate driver events for companies using Poisson inter-arrival and weighted sampling.
        
        Args:
            companies: List of eligible company_ids
            config: Configuration with drivers_per_company and event_rate_per_driver
            interval_start: Start of interval
            interval_end: End of interval
            seed: Random seed for reproducibility
            
        Returns:
            List of DriverEventRecord instances with timestamps in [interval_start, interval_end)
        """
        rng = np.random.RandomState(seed)
        injector = QualityInjector(config.quality_injection, rng)
        events = []
        
        # Event type weights (Option B: Weighted Static)
        event_types = ["start driving", "stopped driving", "delivered"]
        event_type_weights = [0.40, 0.35, 0.25]
        
        truck_counter = 0
        
        for company_id in companies:
            for driver_seq in range(config.drivers_per_company):
                # Poisson event count per driver
                event_count = rng.poisson(config.event_rate_per_driver)
                
                # Generate synthetic IDs
                driver_id = f"DRV-{company_id}-{driver_seq:03d}"
                truck_id = f"TRK-{seed}-{truck_counter:04d}"
                truck_counter += 1
                
                # Generate events for this driver
                for _ in range(event_count):
                    # Weighted categorical sampling for event_type
                    event_type = rng.choice(event_types, p=event_type_weights)
                    
                    # Uniform timestamp within [interval_start, interval_end)
                    interval_duration_seconds = (interval_end - interval_start).total_seconds()
                    offset_seconds = rng.uniform(0, interval_duration_seconds)
                    timestamp = interval_start + timedelta(seconds=offset_seconds)
                    
                    event = DriverEventRecord(
                        driver_id=driver_id,
                        company_id=company_id,
                        truck_id=truck_id,
                        event_type=event_type,
                        timestamp=timestamp
                    )
                    
                    # Inject quality issues if configured
                    event_dict = event.model_dump(mode='json')
                    corrupted_dict = injector.inject_into_driver_event(event_dict, driver_id)
                    
                    # Try to reconstruct - if injection removed required fields, this may fail
                    try:
                        final_event = DriverEventRecord(**corrupted_dict)
                        events.append(final_event)
                    except Exception:
                        # Injected issue made record invalid - skip for now
                        # In production, we'd write malformed JSON directly
                        if self.logger:
                            self.logger.debug(f"Quality injection created invalid record: {corrupted_dict}")
        
        # Log quality injection summary
        if injector.config.enabled and self.logger:
            summary = injector.get_issues_summary()
            self.logger.info(
                f"Quality injection summary",
                metadata={
                    "interval_start": interval_start.isoformat(),
                    "total_events": len(events),
                    "issues_injected": sum(summary.values()),
                    "issue_breakdown": summary
                }
            )
        
        return events
    
    def write_batch(
        self,
        events: List[DriverEventRecord],
        batch_meta: DriverEventBatch,
        output_dir: str
    ) -> None:
        """
        Write batch to disk: events.jsonl and batch_meta.json in batch_id subdirectory.
        
        Args:
            events: List of DriverEventRecord instances
            batch_meta: DriverEventBatch metadata
            output_dir: Base output directory for batches
        """
        batch_dir = Path(output_dir) / batch_meta.batch_id
        batch_dir.mkdir(parents=True, exist_ok=True)
        
        # Write events
        events_file = batch_dir / "events.jsonl"
        with open(events_file, 'w') as f:
            for event in events:
                f.write(event.model_dump_json() + '\n')
        
        # Write batch metadata
        meta_file = batch_dir / "batch_meta.json"
        with open(meta_file, 'w') as f:
            f.write(batch_meta.model_dump_json(indent=2))
        
        if self.logger:
            self.logger.info(
                f"Wrote batch {batch_meta.batch_id}",
                metadata={
                    "batch_id": batch_meta.batch_id,
                    "event_count": len(events),
                    "batch_dir": str(batch_dir)
                }
            )
    
    def update_manifest(self, manifest_path: str, batch_meta: DriverEventBatch) -> None:
        """
        Update cumulative batch manifest.
        
        Args:
            manifest_path: Path to batch_manifest.json
            batch_meta: Metadata for new batch
        """
        manifest_file = Path(manifest_path)
        manifest_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing manifest if present
        if manifest_file.exists():
            with open(manifest_file, 'r') as f:
                data = json.load(f)
                manifest = BatchManifest(**data)
            manifest.total_events += batch_meta.event_count
        else:
            manifest = BatchManifest(
                last_batch_id=batch_meta.batch_id,
                total_events=batch_meta.event_count,
                last_updated=datetime.now(timezone.utc)
            )
        
        manifest.last_batch_id = batch_meta.batch_id
        manifest.last_updated = datetime.now(timezone.utc)
        
        # Write updated manifest
        with open(manifest_file, 'w') as f:
            f.write(manifest.model_dump_json(indent=2))
    
    def generate_single_batch(
        self,
        config: Config,
        output_dir: str,
        companies_file: str,
        seed: int,
        interval_start: datetime,
        interval_end: datetime
    ) -> DriverEventBatch:
        """
        Generate a single batch for the given interval.
        
        Args:
            config: Configuration
            output_dir: Output directory for batches
            companies_file: Path to companies.jsonl
            seed: Random seed
            interval_start: Start of interval
            interval_end: End of interval
            
        Returns:
            DriverEventBatch metadata
        """
        # Get eligible companies (onboarded before interval_start)
        eligible_companies = get_onboarded_companies_before(interval_start, companies_file)
        
        if self.logger:
            self.logger.info(
                f"Generating batch for interval {interval_start.isoformat()} to {interval_end.isoformat()}",
                metadata={
                    "interval_start": interval_start.isoformat(),
                    "interval_end": interval_end.isoformat(),
                    "eligible_companies": len(eligible_companies),
                    "seed": seed
                }
            )
        
        # Generate events
        events = self.generate_driver_events(
            eligible_companies,
            config,
            interval_start,
            interval_end,
            seed
        )
        
        # Create batch metadata
        batch_id = interval_start.strftime("%Y%m%dT%H%M%SZ")
        batch_meta = DriverEventBatch(
            batch_id=batch_id,
            interval_start=interval_start,
            interval_end=interval_end,
            event_count=len(events),
            seed=seed
        )
        
        # Write batch
        self.write_batch(events, batch_meta, output_dir)
        
        # Update manifest
        manifest_path = "data/manifests/batch_manifest.json"
        self.update_manifest(manifest_path, batch_meta)
        
        if self.logger:
            self.logger.info(
                f"Batch {batch_id} complete",
                metadata={
                    "batch_id": batch_id,
                    "event_count": len(events),
                    "eligible_companies": len(eligible_companies)
                }
            )
        
        return batch_meta
    
    def run_scheduling_loop(
        self,
        config: Config,
        output_dir: str,
        companies_file: str,
        seed: int,
        interval_minutes: int = 15
    ) -> None:
        """
        Run continuous scheduling loop, generating batches at interval boundaries.
        
        Args:
            config: Configuration
            output_dir: Output directory for batches
            companies_file: Path to companies.jsonl
            seed: Base random seed
            interval_minutes: Interval duration in minutes
        """
        if self.logger:
            self.logger.info(
                f"Starting scheduling loop with {interval_minutes}-minute intervals",
                metadata={"interval_minutes": interval_minutes}
            )
        
        batch_counter = 0
        
        while not self.shutdown_requested:
            now = datetime.now(timezone.utc)
            interval_start, interval_end = self.compute_interval_bounds(now, interval_minutes)
            
            # If we're before the next interval boundary, sleep until then
            if now < interval_end:
                sleep_seconds = (interval_end - now).total_seconds()
                if self.logger:
                    self.logger.info(
                        f"Sleeping until next interval boundary",
                        metadata={
                            "sleep_seconds": sleep_seconds,
                            "next_boundary": interval_end.isoformat()
                        }
                    )
                time.sleep(min(sleep_seconds, 60))  # Check shutdown every minute
                continue
            
            # Generate batch for the just-completed interval
            batch_seed = seed + batch_counter
            self.generate_single_batch(
                config,
                output_dir,
                companies_file,
                batch_seed,
                interval_start,
                interval_end
            )
            
            batch_counter += 1
    
    def generate(
        self,
        config_path: str,
        output_dir: str,
        companies_file: str,
        provided_seed: Optional[int] = None,
        interval_minutes: int = 15,
        trigger_now: bool = False
    ) -> None:
        """
        Main generation orchestration.
        
        Args:
            config_path: Path to configuration file
            output_dir: Base output directory for batches
            companies_file: Path to companies.jsonl
            provided_seed: Optional explicit seed
            interval_minutes: Interval duration in minutes
            trigger_now: If True, generate single batch immediately; if False, run scheduling loop
        """
        # Setup
        config = self.load_config(config_path)
        log_file = Path("data/manifests/logs") / datetime.now(timezone.utc).strftime("%Y-%m-%d") / "driver_event_generator.log.jsonl"
        self.setup_logging("driver_event_generator", str(log_file))
        
        seed = self.get_seed("data/manifests/seed_manifest.json", provided_seed)
        
        if trigger_now:
            # Generate single batch for current/most recent interval
            now = datetime.now(timezone.utc)
            interval_start, interval_end = self.compute_interval_bounds(now, interval_minutes)
            self.generate_single_batch(config, output_dir, companies_file, seed, interval_start, interval_end)
        else:
            # Run continuous loop
            self.run_scheduling_loop(config, output_dir, companies_file, seed, interval_minutes)


def main():
    """CLI entry point for driver event generator."""
    parser = argparse.ArgumentParser(
        description="Generate 15-minute driver event batches with Poisson inter-arrival",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate single batch immediately
  python -m src.generators.driver_event_generator --config src/config/config.base.yaml --output data/raw/events --companies data/raw/companies.jsonl --now
  
  # Run continuous scheduling loop (generate batches at 15-minute boundaries)
  python -m src.generators.driver_event_generator --config src/config/config.base.yaml --output data/raw/events --companies data/raw/companies.jsonl
  
  # Custom seed
  python -m src.generators.driver_event_generator --config src/config/config.base.yaml --output data/raw/events --companies data/raw/companies.jsonl --seed 42 --now
        """
    )
    
    parser.add_argument(
        '--config',
        required=True,
        help='Path to configuration YAML or JSON file'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Base output directory for batch subdirectories'
    )
    parser.add_argument(
        '--companies',
        required=True,
        help='Path to companies.jsonl file for coordination'
    )
    parser.add_argument(
        '--seed',
        type=int,
        help='Random seed for reproducibility (optional)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=15,
        help='Interval duration in minutes (default: 15)'
    )
    parser.add_argument(
        '--now',
        action='store_true',
        help='Generate single batch immediately instead of running scheduling loop'
    )
    
    args = parser.parse_args()
    
    try:
        generator = DriverEventGenerator()
        generator.generate(
            config_path=args.config,
            output_dir=args.output,
            companies_file=args.companies,
            provided_seed=args.seed,
            interval_minutes=args.interval,
            trigger_now=args.now
        )
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
