"""Health aggregation service: produces read-only health snapshot without side-effects."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

from src.generators.lifecycle import GeneratorLifecycle


@dataclass
class HealthSnapshot:
    status: str
    timestamp: str
    generation_mode: str  # "production" or "emulated"
    uptime_seconds: float
    start_time: str
    company_batches: int
    driver_batches: int
    last_company_time: Optional[str]
    last_driver_time: Optional[str]
    paused: bool
    shutdown_requested: bool
    verification: Optional[Dict[str, Any]] = None
    emulated_config: Optional[Dict[str, Any]] = None  # Only present when mode=emulated


class HealthAggregator:
    def __init__(self, lifecycle: GeneratorLifecycle, state_file: str, config_path: Optional[str] = None) -> None:
        self.lifecycle = lifecycle
        self.state_file = Path(state_file)
        self.config_path = config_path
        self.start_time = datetime.now(timezone.utc)

    def aggregate(self, verification: Optional[Dict[str, Any]] = None) -> HealthSnapshot:
        data: Dict[str, Any] = {}
        if self.state_file.exists():
            try:
                import json
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
            except Exception:  # pragma: no cover - defensive
                data = {}
        
        # Load config to determine mode
        generation_mode = "production"
        emulated_config_data = None
        if self.config_path:
            try:
                from src.generators.config import Config
                import yaml
                with open(self.config_path, 'r') as f:
                    config_dict = yaml.safe_load(f)
                config = Config(**config_dict)
                if config.emulated_mode.enabled:
                    generation_mode = "emulated"
                    # Parse intervals to get seconds
                    import isodate
                    from datetime import timedelta
                    company_interval = isodate.parse_duration(config.emulated_mode.company_batch_interval)
                    driver_interval = isodate.parse_duration(config.emulated_mode.driver_batch_interval)
                    emulated_config_data = {
                        "company_interval_seconds": int(company_interval.total_seconds()) if isinstance(company_interval, timedelta) else 10,
                        "driver_interval_seconds": int(driver_interval.total_seconds()) if isinstance(driver_interval, timedelta) else 10,
                        "companies_per_batch": config.emulated_mode.companies_per_batch,
                        "events_per_batch_range": [
                            config.emulated_mode.events_per_batch_min,
                            config.emulated_mode.events_per_batch_max
                        ]
                    }
            except Exception:  # pragma: no cover - defensive
                pass
        
        now = datetime.now(timezone.utc)
        uptime = (now - self.start_time).total_seconds()
        status = "paused" if self.lifecycle.paused else "running"
        return HealthSnapshot(
            status=status,
            timestamp=now.isoformat(),
            generation_mode=generation_mode,
            uptime_seconds=round(uptime, 2),
            start_time=self.start_time.isoformat(),
            company_batches=int(data.get("last_company_batch", 0) or 0),
            driver_batches=int(data.get("last_driver_batch", 0) or 0),
            last_company_time=data.get("last_company_time"),
            last_driver_time=data.get("last_driver_time"),
            paused=self.lifecycle.paused,
            shutdown_requested=getattr(self.lifecycle, 'should_exit', False),
            verification=verification,
            emulated_config=emulated_config_data,
        )
