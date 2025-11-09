from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime, timezone


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()

@dataclass
class IngestionFileStats:
    source_file: str
    raw_count: int
    accepted_count: int
    rejected_count: int
    duplicate_count: int
    malformed_count: int

@dataclass
class IngestionManifest:
    run_id: str
    started_at: str = field(default_factory=_ts)
    finished_at: str | None = None
    status: str = "IN_PROGRESS"
    files: List[IngestionFileStats] = field(default_factory=list)
    totals: Dict[str, int] = field(default_factory=dict)

    def finalize(self):
        self.finished_at = _ts()
        self.status = "SUCCESS"
        self.totals = {
            "raw": sum(f.raw_count for f in self.files),
            "accepted": sum(f.accepted_count for f in self.files),
            "rejected": sum(f.rejected_count for f in self.files),
            "duplicates": sum(f.duplicate_count for f in self.files),
            "malformed": sum(f.malformed_count for f in self.files),
        }

@dataclass
class EnrichmentManifest:
    run_id: str
    started_at: str = field(default_factory=_ts)
    finished_at: str | None = None
    status: str = "IN_PROGRESS"
    matched_count: int = 0
    unmatched_company_ids: List[str] = field(default_factory=list)
    total_events: int = 0

    def finalize(self):
        self.finished_at = _ts()
        self.status = "SUCCESS"
