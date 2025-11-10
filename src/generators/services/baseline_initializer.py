"""Baseline data initialization service.

Responsible for ensuring companies baseline and at least one driver events batch
exist. Designed to be idempotent and safe to call on every resume.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, List, Dict

import yaml


@dataclass
class BaselineInitResult:
    companies_created: int
    driver_batches_created: int
    actions: List[Dict[str, str]]
    errors: List[str]
    timestamp: str


class BaselineInitializer:
    """Encapsulates baseline creation logic without mutating external state files."""

    def __init__(self, config_path: str, companies_file: str, events_dir: str) -> None:
        self.config_path = Path(config_path)
        self.companies_file = Path(companies_file)
        self.events_dir = Path(events_dir)

    def ensure_baseline(self) -> BaselineInitResult:
        """Ensure baseline data exists, generating missing pieces.

        Returns a structured result describing actions taken.
        """
        actions: List[Dict[str, str]] = []
        errors: List[str] = []
        companies_created = 0
        driver_batches_created = 0

        if not self.config_path.exists():
            return BaselineInitResult(
                companies_created=0,
                driver_batches_created=0,
                actions=actions,
                errors=[f"missing_config:{self.config_path}"],
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

        # Load minimal config
        try:
            with open(self.config_path, "r") as f:
                cfg = yaml.safe_load(f) or {}
            company_count = int(cfg.get("number_of_companies", 0) or 0)
            seed_value = int(cfg.get("seed", 42))
        except Exception as e:  # pragma: no cover - defensive
            errors.append(f"config_error:{e}")
            return BaselineInitResult(
                companies_created=0,
                driver_batches_created=0,
                actions=actions,
                errors=errors,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

        # Ensure directories
        self.companies_file.parent.mkdir(parents=True, exist_ok=True)
        self.events_dir.mkdir(parents=True, exist_ok=True)

        need_companies = (not self.companies_file.exists()) or self.companies_file.stat().st_size == 0
        need_events = (not self.events_dir.exists()) or (len(list(self.events_dir.glob("*"))) == 0)

        if need_companies and company_count > 0:
            try:
                from src.generators.company_generator import CompanyGenerator
                gen = CompanyGenerator()
                # Load config to pass to generate_companies
                from src.generators.config import Config
                with open(str(self.config_path), 'r') as f:
                    config_dict = yaml.safe_load(f)
                config = Config(**config_dict)
                seed = gen.get_seed("data/manifests/seed_manifest.json", seed_value)
                companies, corrupted = gen.generate_companies(company_count, seed, config)
                gen.write_companies_jsonl(companies, corrupted, str(self.companies_file))
                companies_created = company_count
                actions.append({"companies": str(company_count)})
            except Exception as e:
                errors.append(f"companies_error:{e}")

        if need_events:
            try:
                from src.generators.driver_event_generator import DriverEventGenerator
                drv = DriverEventGenerator()
                driver_cfg = drv.load_config(str(self.config_path))
                seed = drv.get_seed("data/manifests/seed_manifest.json", seed_value)
                now = datetime.now(timezone.utc)
                # For baseline initialization, use the current time as interval_start
                # so that newly created companies (created_at <= now) are eligible.
                # This ensures the batch includes all baseline companies.
                interval_duration_minutes = 15
                interval_start = now
                interval_end = now + timedelta(minutes=interval_duration_minutes)
                drv.generate_single_batch(
                    driver_cfg,
                    str(self.events_dir),
                    str(self.companies_file),
                    seed,
                    interval_start,
                    interval_end,
                )
                driver_batches_created = 1
                actions.append({"driver_batch": "1"})
            except Exception as e:
                errors.append(f"driver_error:{e}")

        return BaselineInitResult(
            companies_created=companies_created,
            driver_batches_created=driver_batches_created,
            actions=actions,
            errors=errors,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
