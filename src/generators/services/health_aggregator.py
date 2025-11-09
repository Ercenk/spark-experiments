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
    uptime_seconds: float
    start_time: str
    company_batches: int
    driver_batches: int
    last_company_time: Optional[str]
    last_driver_time: Optional[str]
    paused: bool
    shutdown_requested: bool
    verification: Optional[Dict[str, Any]] = None


class HealthAggregator:
    def __init__(self, lifecycle: GeneratorLifecycle, state_file: str) -> None:
        self.lifecycle = lifecycle
        self.state_file = Path(state_file)
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
        now = datetime.now(timezone.utc)
        uptime = (now - self.start_time).total_seconds()
        status = "paused" if self.lifecycle.paused else "running"
        return HealthSnapshot(
            status=status,
            timestamp=now.isoformat(),
            uptime_seconds=round(uptime, 2),
            start_time=self.start_time.isoformat(),
            company_batches=int(data.get("last_company_batch", 0) or 0),
            driver_batches=int(data.get("last_driver_batch", 0) or 0),
            last_company_time=data.get("last_company_time"),
            last_driver_time=data.get("last_driver_time"),
            paused=self.lifecycle.paused,
            shutdown_requested=getattr(self.lifecycle, 'should_exit', False),
            verification=verification,
        )
