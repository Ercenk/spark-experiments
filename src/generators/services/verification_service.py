"""Verification service to confirm baseline artifacts exist and gather metadata."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict


@dataclass
class VerificationReport:
    timestamp: str
    companies_exists: bool
    companies_size: int
    events_exists: bool
    event_file_count: int
    missing: List[str]
    details: Dict[str, str]


class VerificationService:
    def __init__(self, companies_file: str, events_dir: str) -> None:
        self.companies_file = Path(companies_file)
        self.events_dir = Path(events_dir)

    def verify(self) -> VerificationReport:
        companies_exists = self.companies_file.exists() and self.companies_file.stat().st_size > 0
        companies_size = self.companies_file.stat().st_size if self.companies_file.exists() else 0
        events_exists = self.events_dir.exists() and any(self.events_dir.iterdir())
        event_count = len(list(self.events_dir.glob('*'))) if self.events_dir.exists() else 0
        missing: List[str] = []
        if not companies_exists:
            missing.append(str(self.companies_file))
        if not events_exists:
            missing.append(str(self.events_dir))
        details: Dict[str, str] = {}
        if companies_exists:
            details["companies_mtime"] = datetime.fromtimestamp(self.companies_file.stat().st_mtime, tz=timezone.utc).isoformat()
        if events_exists:
            latest = max((f.stat().st_mtime for f in self.events_dir.iterdir() if f.is_file()), default=None)
            if latest:
                details["events_latest_mtime"] = datetime.fromtimestamp(latest, tz=timezone.utc).isoformat()
        return VerificationReport(
            timestamp=datetime.now(timezone.utc).isoformat(),
            companies_exists=companies_exists,
            companies_size=companies_size,
            events_exists=events_exists,
            event_file_count=event_count,
            missing=missing,
            details=details,
        )
