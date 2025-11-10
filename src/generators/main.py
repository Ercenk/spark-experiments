"""Unified entry point for continuous generator execution."""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from src.generators.lifecycle import GeneratorLifecycle
from src.generators.orchestrator import GeneratorOrchestrator


class GeneratorState:
    """Manages persistent state for generators."""
    
    def __init__(self, state_file: str = "data/manifests/generator_state.json"):
        """
        Initialize state manager.
        
        Args:
            state_file: Path to state persistence file
        """
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
    
    def save(self, lifecycle: GeneratorLifecycle, metadata: dict) -> None:
        """
        Save current state to disk.
        
        Args:
            lifecycle: Lifecycle manager
            metadata: Additional metadata (batch counts, timestamps, etc.)
        """
        state = {
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "lifecycle": lifecycle.get_state(),
            **metadata
        }
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load(self) -> Optional[dict]:
        """
        Load state from disk.
        
        Returns:
            State dictionary or None if file doesn't exist
        """
        if not self.state_file.exists():
            return None
        
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None


def run_company_generator_continuous(
    config_path: str,
    output_path: str,
    lifecycle: GeneratorLifecycle,
    state: GeneratorState,
    logger=None
):
    """
    Run company generator in continuous mode with lifecycle integration.
    
    Args:
        config_path: Path to configuration file
        output_path: Path to companies.jsonl output
        lifecycle: Lifecycle manager
        state: State manager
        logger: Optional logger
    """
    from src.generators.company_generator import CompanyGenerator
    from src.generators.orchestrator import GeneratorOrchestrator
    from src.generators.config import Config
    import yaml
    from datetime import timedelta
    import isodate
    
    if logger:
        logger.info(
            "Starting company generator in continuous mode",
            metadata={
                "config_path": config_path,
                "output_path": output_path
            }
        )
    
    generator = CompanyGenerator()
    generator.logger = logger
    
    # Load config
    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f)
    config = Config(**config_data)
    
    # Log generation mode at startup
    mode_str = "emulated" if config.emulated_mode.enabled else "production"
    if logger:
        logger.info(
            f"Starting company generator in {mode_str} mode",
            metadata={
                "mode": mode_str,
                "interval": config.active_company_interval,
                "batch_size": config.active_company_count
            }
        )
    
    # Parse active company interval (uses emulated or production based on config)
    interval_duration = isodate.parse_duration(config.active_company_interval)
    if not isinstance(interval_duration, timedelta):
        interval_duration = timedelta(hours=1)  # Default fallback
    
    seed = generator.get_seed("data/manifests/seed_manifest.json", config.seed)
    batch_counter = 0
    
    # Check if this is initial startup (no companies exist)
    output_file = Path(output_path)
    if not output_file.exists() or output_file.stat().st_size == 0:
        if logger:
            logger.info(
                "Initial startup detected - generating first company batch",
                metadata={"output_path": output_path, "count": config.active_company_count}
            )
        companies = generator.generate_companies(config.active_company_count, seed + batch_counter, config)
        written_count = generator.write_companies_jsonl(companies, output_path)
        batch_counter += 1
        state.save(lifecycle, {"last_company_batch": batch_counter, "last_company_time": datetime.now(timezone.utc).isoformat()})
        if logger:
            logger.info(
                f"Initial company batch generated: {written_count} companies written",
                metadata={"batch_counter": 0, "written_count": written_count}
            )
    
    while not lifecycle.should_shutdown():
        # Wait if paused
        if not lifecycle.wait_if_paused():
            break
        
        # Generate companies
        batch_start_time = datetime.now(timezone.utc)
        companies, corrupted_companies = generator.generate_companies(config.active_company_count, seed + batch_counter, config)
        written_count = generator.write_companies_jsonl(companies, corrupted_companies, output_path)
        batch_duration = (datetime.now(timezone.utc) - batch_start_time).total_seconds()
        
        mode_str = "emulated" if config.emulated_mode.enabled else "production"
        if logger:
            logger.info(
                f"Company batch {batch_counter} generated ({mode_str} mode): {written_count} companies written",
                metadata={
                    "batch_counter": batch_counter,
                    "mode": mode_str,
                    "generated_count": len(companies),
                    "corrupted_count": len(corrupted_companies),
                    "written_count": written_count,
                    "discarded_count": len(companies) - written_count,
                    "batch_duration_seconds": round(batch_duration, 3),
                    "seed": seed + batch_counter,
                    "output_path": output_path
                }
            )
        
        batch_counter += 1
        
        # Save state
        state.save(lifecycle, {"last_company_batch": batch_counter, "last_company_time": datetime.now(timezone.utc).isoformat()})
        
        # Wait for next interval
        next_time = datetime.now(timezone.utc) + interval_duration
        if logger:
            logger.info(
                f"Waiting for next company generation interval",
                metadata={
                    "next_generation_time": next_time.isoformat(),
                    "wait_duration_seconds": round(interval_duration.total_seconds(), 0),
                    "completed_batches": batch_counter
                }
            )
        if not GeneratorOrchestrator.wait_for_next_interval(next_time, lifecycle, emulated_mode=config.emulated_mode.enabled):
            if logger:
                logger.info("Company generator shutdown requested")
            break


def run_driver_generator_continuous(
    config_path: str,
    output_dir: str,
    companies_file: str,
    lifecycle: GeneratorLifecycle,
    state: GeneratorState,
    logger=None
):
    """
    Run driver event generator in continuous mode with lifecycle integration.
    
    Args:
        config_path: Path to configuration file
        output_dir: Output directory for batches
        companies_file: Path to companies.jsonl
        lifecycle: Lifecycle manager
        state: State manager
        logger: Optional logger
    """
    from src.generators.driver_event_generator import DriverEventGenerator
    from src.generators.orchestrator import GeneratorOrchestrator
    import isodate
    from datetime import timedelta
    
    generator = DriverEventGenerator()
    generator.logger = logger
    
    config = generator.load_config(config_path)
    seed = generator.get_seed("data/manifests/seed_manifest.json", config.seed)
    
    # Log generation mode at startup
    mode_str = "emulated" if config.emulated_mode.enabled else "production"
    
    # Parse active driver interval (uses emulated or production based on config)
    interval_duration = isodate.parse_duration(config.active_driver_interval)
    if not isinstance(interval_duration, timedelta):
        interval_duration = timedelta(minutes=15)  # Default fallback
    interval_seconds = interval_duration.total_seconds()
    
    if logger:
        logger.info(
            f"Starting driver event generator in {mode_str} mode",
            metadata={
                "mode": mode_str,
                "config_path": config_path,
                "output_dir": output_dir,
                "companies_file": companies_file,
                "interval": config.active_driver_interval,
                "interval_seconds": interval_seconds
            }
        )
    
    batch_counter = 0
    
    # Check if this is initial startup (no batches exist)
    output_path = Path(output_dir)
    has_existing_batches = output_path.exists() and any(output_path.iterdir())
    
    if not has_existing_batches:
        if logger:
            logger.info(
                "Initial startup detected - generating first driver event batch immediately",
                metadata={"output_dir": output_dir}
            )
        # Generate batch for current/most recent interval immediately
        # For initial startup, use current time as cutoff so newly created companies are included
        now = datetime.now(timezone.utc)
        interval_start = GeneratorOrchestrator.align_to_interval(now, interval_seconds)
        interval_end = interval_start + interval_duration
        
        batch_seed = seed + batch_counter
        batch_start_time = datetime.now(timezone.utc)
        
        # Get eligible companies (use 'now' instead of interval_start for initial batch)
        from src.generators.coordination import get_onboarded_companies_before as coord_get_companies
        eligible_companies = coord_get_companies(now, companies_file)
        
        # Apply emulated mode batch size limits if enabled
        if config.emulated_mode.enabled:
            max_companies = config.emulated_mode.companies_per_batch
            eligible_companies = eligible_companies[:max_companies]
        
        if logger:
            logger.info(
                "Generating batch for interval with initial startup eligible companies",
                metadata={
                    "interval_start": interval_start.isoformat(),
                    "interval_end": interval_end.isoformat(),
                    "eligible_companies": len(eligible_companies),
                    "seed": batch_seed
                }
            )
        
        # Adjust event rate for emulated mode if needed
        effective_config = config
        if config.emulated_mode.enabled and len(eligible_companies) > 0:
            # Scale event_rate_per_driver to hit target event range
            target_events = (config.emulated_mode.events_per_batch_min + 
                             config.emulated_mode.events_per_batch_max) / 2
            expected_drivers = len(eligible_companies) * config.drivers_per_company
            if expected_drivers > 0:
                adjusted_rate = target_events / expected_drivers
                # Create temporary config with adjusted rate
                effective_config = config.model_copy(deep=True)
                effective_config.event_rate_per_driver = max(0.1, adjusted_rate)
        
        # Generate events using the eligible companies
        events = generator.generate_driver_events(
            eligible_companies,
            effective_config,
            interval_start,
            interval_end,
            batch_seed
        )
        
        # Truncate if exceeded max in emulated mode
        if config.emulated_mode.enabled and len(events) > config.emulated_mode.events_per_batch_max:
            events = events[:config.emulated_mode.events_per_batch_max]
        
        # Create batch metadata
        batch_id = interval_start.strftime("%Y%m%dT%H%M%SZ")
        from src.generators.models import DriverEventBatch
        batch_meta = DriverEventBatch(
            batch_id=batch_id,
            interval_start=interval_start,
            interval_end=interval_end,
            event_count=len(events),
            seed=batch_seed
        )
        
        # Write batch
        generator.write_batch(events, batch_meta, output_dir)
        
        # Update manifest
        manifest_path = "data/manifests/batch_manifest.json"
        generator.update_manifest(manifest_path, batch_meta)
        
        batch_duration = (datetime.now(timezone.utc) - batch_start_time).total_seconds()
        
        if logger:
            logger.info(
                f"Initial driver batch generated ({mode_str} mode): {batch_meta.event_count} events",
                metadata={
                    "batch_counter": batch_counter,
                    "mode": mode_str,
                    "batch_id": batch_meta.batch_id,
                    "event_count": batch_meta.event_count,
                    "interval_start": interval_start.isoformat(),
                    "interval_end": interval_end.isoformat(),
                    "batch_duration_seconds": round(batch_duration, 3),
                    "seed": batch_seed,
                    "output_dir": output_dir
                }
            )
        
        batch_counter += 1
        
        # Save state
        state.save(lifecycle, {
            "last_driver_batch": batch_counter,
            "last_driver_time": datetime.now(timezone.utc).isoformat(),
            "last_interval_end": interval_end.isoformat()
        })
    
    while not lifecycle.should_shutdown():
        # Wait if paused
        if not lifecycle.wait_if_paused():
            break
        
        # Compute interval using align_to_interval for second-level precision
        now = datetime.now(timezone.utc)
        interval_start = GeneratorOrchestrator.align_to_interval(now, interval_seconds)
        interval_end = interval_start + interval_duration
        
        # Wait until interval end if we're in the middle of an interval
        if now < interval_end:
            wait_seconds = (interval_end - now).total_seconds()
            if logger:
                logger.info(
                    f"Waiting for interval boundary",
                    metadata={
                        "current_time": now.isoformat(),
                        "interval_end": interval_end.isoformat(),
                        "wait_seconds": round(wait_seconds, 1),
                        "completed_batches": batch_counter
                    }
                )
            if not GeneratorOrchestrator.wait_for_next_interval(interval_end, lifecycle, emulated_mode=config.emulated_mode.enabled):
                if logger:
                    logger.info("Driver generator shutdown requested")
                break
            continue
        
        # Generate batch
        batch_seed = seed + batch_counter
        batch_start_time = datetime.now(timezone.utc)
        
        # Get eligible companies
        from src.generators.coordination import get_onboarded_companies_before as coord_get_companies
        eligible_companies = coord_get_companies(interval_start, companies_file)
        
        # Apply emulated mode batch size limits if enabled
        if config.emulated_mode.enabled:
            max_companies = config.emulated_mode.companies_per_batch
            eligible_companies = eligible_companies[:max_companies]
        
        # Adjust event rate for emulated mode if needed
        effective_config = config
        if config.emulated_mode.enabled and len(eligible_companies) > 0:
            # Scale event_rate_per_driver to hit target event range
            target_events = (config.emulated_mode.events_per_batch_min + 
                             config.emulated_mode.events_per_batch_max) / 2
            expected_drivers = len(eligible_companies) * config.drivers_per_company
            if expected_drivers > 0:
                adjusted_rate = target_events / expected_drivers
                # Create temporary config with adjusted rate
                effective_config = config.model_copy(deep=True)
                effective_config.event_rate_per_driver = max(0.1, adjusted_rate)
        
        # Generate events
        events = generator.generate_driver_events(
            eligible_companies,
            effective_config,
            interval_start,
            interval_end,
            batch_seed
        )
        
        # Truncate if exceeded max in emulated mode
        if config.emulated_mode.enabled and len(events) > config.emulated_mode.events_per_batch_max:
            events = events[:config.emulated_mode.events_per_batch_max]
        
        # Create batch metadata
        batch_id = interval_start.strftime("%Y%m%dT%H%M%SZ")
        from src.generators.models import DriverEventBatch
        batch_meta = DriverEventBatch(
            batch_id=batch_id,
            interval_start=interval_start,
            interval_end=interval_end,
            event_count=len(events),
            seed=batch_seed
        )
        
        # Write batch
        generator.write_batch(events, batch_meta, output_dir)
        
        # Update manifest
        manifest_path = "data/manifests/batch_manifest.json"
        generator.update_manifest(manifest_path, batch_meta)
        
        batch_duration = (datetime.now(timezone.utc) - batch_start_time).total_seconds()
        
        if logger:
            logger.info(
                f"Driver batch {batch_counter} generated ({mode_str} mode): {batch_meta.event_count} events for interval [{interval_start.strftime('%H:%M:%S')}-{interval_end.strftime('%H:%M:%S')}]",
                metadata={
                    "batch_counter": batch_counter,
                    "mode": mode_str,
                    "batch_id": batch_meta.batch_id,
                    "event_count": batch_meta.event_count,
                    "eligible_companies": len(eligible_companies) if not config.emulated_mode.enabled else config.emulated_mode.companies_per_batch,
                    "interval_start": interval_start.isoformat(),
                    "interval_end": interval_end.isoformat(),
                    "batch_duration_seconds": round(batch_duration, 3),
                    "seed": batch_seed,
                    "output_dir": output_dir
                }
            )
        
        batch_counter += 1
        
        # Save state
        state.save(lifecycle, {
            "last_driver_batch": batch_counter,
            "last_driver_time": datetime.now(timezone.utc).isoformat(),
            "last_interval_end": interval_end.isoformat()
        })


def main():
    """Main entry point for unified generator orchestration."""
    parser = argparse.ArgumentParser(
        description="Unified generator orchestrator with lifecycle management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run both generators continuously
  python -m src.generators.main --mode both --config src/config/config.base.yaml
  
  # Run only company generator
  python -m src.generators.main --mode company --config src/config/config.base.yaml --output data/raw/companies.jsonl
  
  # Run only driver generator
  python -m src.generators.main --mode driver --config src/config/config.base.yaml --output data/raw/events --companies data/raw/companies.jsonl
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['company', 'driver', 'both'],
        required=True,
        help='Generator mode: company, driver, or both'
    )
    parser.add_argument(
        '--config',
        required=True,
        help='Path to configuration file'
    )
    parser.add_argument(
        '--output',
        help='Output path (companies.jsonl for company mode, directory for driver mode)'
    )
    parser.add_argument(
        '--companies',
        help='Path to companies.jsonl (required for driver mode)'
    )
    
    args = parser.parse_args()
    
    # Initialize lifecycle and state
    lifecycle = GeneratorLifecycle()
    state = GeneratorState()
    
    # Setup logging
    from src.logging.json_logger import JSONLogger
    log_file = Path("data/manifests/logs") / datetime.now(timezone.utc).strftime("%Y-%m-%d") / "orchestrator.log.jsonl"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger = JSONLogger(component="orchestrator", log_file=str(log_file))
    
    # Register signal handlers
    lifecycle.register_signal_handlers(logger)
    
    # Start health server
    from src.generators.health import HealthServer
    # Optional new blueprint-based API (not yet replacing HealthServer routes)
    try:
        from src.generators.api import create_api_blueprint  # type: ignore
        _HAVE_BLUEPRINT = True
    except Exception:  # pragma: no cover - defensive
        _HAVE_BLUEPRINT = False
    # Provide config & data paths to enable auto reinit in resume
    health_server = HealthServer(
        port=8000,
        lifecycle=lifecycle,
        config_path=args.config,
        companies_file=(args.companies if args.companies else "data/raw/companies.jsonl"),
        driver_events_dir=(args.output if args.mode == 'driver' else "data/raw/events")
    )
    health_server.start_background()
    logger.info("Health server started on port 8000 (mapped to 18000 externally) with pause/resume endpoints")

    # Attach new blueprint for decoupled handlers (experimental)
    if _HAVE_BLUEPRINT:
        try:
            bp = create_api_blueprint(
                lifecycle=lifecycle,
                config_path=args.config,
                companies_file=(args.companies if args.companies else "data/raw/companies.jsonl"),
                events_dir=(args.output if args.mode == 'driver' else "data/raw/events"),
                state_file="data/manifests/generator_state.json",
                logs_root="data/manifests/logs",
            )
            health_server.app.register_blueprint(bp, url_prefix="/api")
            logger.info("Experimental API blueprint mounted at /api")
        except Exception as e:  # pragma: no cover - defensive
            logger.error(f"Failed to mount API blueprint: {e}")
    
    # Load previous state
    prev_state = state.load()
    if prev_state and prev_state.get("lifecycle", {}).get("paused"):
        lifecycle.paused = True
        lifecycle.pause_event.clear()
        logger.info("Recovered paused state from previous run")
    
    logger.info(f"Starting generator in {args.mode} mode")
    
    # Create orchestrator
    orchestrator = GeneratorOrchestrator(lifecycle)
    
    # Add generators based on mode
    if args.mode in ['company', 'both']:
        output_path = args.output if args.output else "data/raw/companies.jsonl"
        orchestrator.add_generator(
            "company-generator",
            run_company_generator_continuous,
            (args.config, output_path, lifecycle, state, logger)
        )
    
    if args.mode in ['driver', 'both']:
        output_dir = args.output if args.output else "data/raw/events"
        companies_file = args.companies if args.companies else "data/raw/companies.jsonl"
        orchestrator.add_generator(
            "driver-generator",
            run_driver_generator_continuous,
            (args.config, output_dir, companies_file, lifecycle, state, logger)
        )
    
    # Start generators
    try:
        orchestrator.start()
        logger.info("All generators started")
        
        # Wait for completion
        orchestrator.wait()
        
        logger.info("All generators stopped")
    except Exception as e:
        logger.error(f"Error during execution: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
