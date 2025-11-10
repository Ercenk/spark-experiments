"""Company onboarding generator."""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from src.generators.base import BaseGenerator
from src.generators.config import Config
from src.generators.models import Company
from src.generators.injector import QualityInjector


class CompanyGenerator(BaseGenerator):
    """
    Generator for company onboarding records.
    
    Creates companies with unique IDs, fixed US geography, and active status.
    Supports reproducible generation via seed.
    """
    
    def generate_companies(self, count: int, seed: int, config: Config) -> List[Company]:
        """
        Generate company records.
        
        Args:
            count: Number of companies to generate
            seed: Random seed for reproducibility (affects UUID generation indirectly via created_at variance)
            config: Configuration including quality injection settings
            
        Returns:
            List of Company instances
            
        Note:
            Each company gets a unique UUID. The seed primarily affects
            timestamp jitter and ordering for reproducibility.
        """
        import random
        import numpy as np
        
        random.seed(seed)
        rng = np.random.RandomState(seed)
        injector = QualityInjector(config.quality_injection, rng)
        
        companies = []
        base_time = datetime.now(timezone.utc)
        
        for i in range(count):
            # Add small jitter to created_at for realism (< 1 second)
            jitter_ms = random.randint(0, 999)
            created_at = base_time.replace(microsecond=jitter_ms * 1000)
            
            company = Company(created_at=created_at)
            
            # Inject quality issues if configured
            company_dict = company.model_dump(mode='json')
            corrupted_dict = injector.inject_into_company(company_dict)
            
            # Try to reconstruct - if injection removed required fields, may fail
            try:
                final_company = Company(**corrupted_dict)
                companies.append(final_company)
            except Exception:
                # Invalid company - skip for now (in production, write malformed JSON)
                if self.logger:
                    self.logger.debug(f"Quality injection created invalid company: {corrupted_dict}")
        
        # Log quality injection summary
        if injector.config.enabled and self.logger:
            summary = injector.get_issues_summary()
            self.logger.info(
                f"Quality injection summary for companies",
                metadata={
                    "total_companies": len(companies),
                    "issues_injected": sum(summary.values()),
                    "issue_breakdown": summary
                }
            )
        
        return companies
    
    def write_companies_jsonl(self, companies: List[Company], output_path: str) -> int:
        """
        Write companies to JSON Lines file (append-only, reject duplicates).
        
        Args:
            companies: List of Company instances to write
            output_path: Path to output companies.jsonl file
            
        Returns:
            Number of companies successfully written (excludes duplicates)
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing company IDs if file exists
        existing_ids = set()
        if output_file.exists():
            with open(output_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            data = json.loads(line)
                            existing_ids.add(data.get('company_id'))
                        except json.JSONDecodeError:
                            continue
        
        # Write new companies, skip duplicates
        written_count = 0
        discarded_count = 0
        
        with open(output_file, 'a') as f:
            for company in companies:
                if company.company_id in existing_ids:
                    discarded_count += 1
                    if self.logger:
                        self.logger.warn(
                            f"Duplicate company_id discarded: {company.company_id}",
                            metadata={"company_id": company.company_id}
                        )
                    continue
                
                f.write(company.model_dump_json() + '\n')
                existing_ids.add(company.company_id)
                written_count += 1
        
        if self.logger:
            self.logger.info(
                f"Wrote {written_count} companies, discarded {discarded_count} duplicates",
                metadata={
                    "written": written_count,
                    "discarded": discarded_count,
                    "output_path": output_path
                }
            )
        
        return written_count
    
    def write_dataset_descriptor(self, descriptor_path: str, config: Config, seed: int) -> None:
        """
        Write dataset descriptor markdown file (once on first run).
        
        Args:
            descriptor_path: Path to dataset.md file
            config: Configuration used for generation
            seed: Seed value used
        """
        descriptor_file = Path(descriptor_path)
        
        # Skip if descriptor already exists
        if descriptor_file.exists():
            return
        
        descriptor_file.parent.mkdir(parents=True, exist_ok=True)
        
        descriptor_content = f"""# Dataset Descriptor

**Generated**: {datetime.now(timezone.utc).isoformat()}
**Seed**: {seed}

## Configuration

- **Companies**: {config.number_of_companies}
- **Drivers per Company**: {config.drivers_per_company}
- **Event Rate per Driver**: {config.event_rate_per_driver} (per 15-min interval)
- **Company Onboarding Interval**: {config.company_onboarding_interval}

## Reproducibility

To reproduce this dataset exactly:
1. Use seed: `{seed}`
2. Apply same configuration parameters above
3. Run company generator followed by driver generator in order

## Notes

- Geography fixed to `US` in initial iteration
- All companies initially active (no deactivation)
- Driver events generated at 15-minute intervals
"""
        
        with open(descriptor_file, 'w') as f:
            f.write(descriptor_content)
        
        if self.logger:
            self.logger.info(
                f"Created dataset descriptor at {descriptor_path}",
                metadata={"descriptor_path": descriptor_path}
            )
    
    def generate(self, config_path: str, output_path: str, provided_seed: Optional[int] = None, count_override: Optional[int] = None) -> None:
        """
        Main generation orchestration.
        
        Args:
            config_path: Path to configuration file
            output_path: Path to output companies.jsonl
            provided_seed: Optional explicit seed
            count_override: Optional override for number_of_companies from config
        """
        # Setup
        config = self.load_config(config_path)
        log_file = Path("data/manifests/logs") / datetime.now(timezone.utc).strftime("%Y-%m-%d") / "company_generator.log.jsonl"
        self.setup_logging("company_generator", str(log_file))
        
        seed = self.get_seed("data/manifests/seed_manifest.json", provided_seed)
        
        # Determine count
        count = count_override if count_override is not None else config.number_of_companies
        
        self.logger.info(
            f"Starting company generation",
            metadata={
                "count": count,
                "seed": seed,
                "config_path": config_path,
                "output_path": output_path
            }
        )
        
        # Generate
        companies = self.generate_companies(count, seed, config)
        
        # Write
        written_count = self.write_companies_jsonl(companies, output_path)
        
        # Write dataset descriptor (once)
        descriptor_path = "data/manifests/dataset.md"
        self.write_dataset_descriptor(descriptor_path, config, seed)
        
        self.logger.info(
            f"Company generation complete",
            metadata={
                "written_count": written_count,
                "total_requested": count
            }
        )


def main():
    """CLI entry point for company generator."""
    parser = argparse.ArgumentParser(
        description="Generate company onboarding records as JSON Lines",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.generators.company_generator --config src/config/config.base.yaml --output data/raw/companies.jsonl
  python -m src.generators.company_generator --config src/config/config.base.yaml --output data/raw/companies.jsonl --seed 42
  python -m src.generators.company_generator --config src/config/config.base.yaml --output data/raw/companies.jsonl --count 50
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
        help='Path to output companies.jsonl file'
    )
    parser.add_argument(
        '--seed',
        type=int,
        help='Random seed for reproducibility (optional, generated if not provided)'
    )
    parser.add_argument(
        '--count',
        type=int,
        help='Number of companies to generate (overrides config value)'
    )
    
    args = parser.parse_args()
    
    try:
        generator = CompanyGenerator()
        generator.generate(
            config_path=args.config,
            output_path=args.output,
            provided_seed=args.seed,
            count_override=args.count
        )
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
