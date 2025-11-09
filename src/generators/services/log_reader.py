"""Log reading service extracted from HealthServer logic."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any


class LogReaderService:
    def __init__(self, logs_root: str) -> None:
        self.logs_root = Path(logs_root)

    def read_logs(
        self,
        limit: int = 100,
        since: Optional[str] = None,
        level: Optional[str] = None,
    ) -> Dict[str, Any]:
        try:
            limit = max(1, min(1000, int(limit)))
        except ValueError:
            limit = 100
        since_dt = None
        if since:
            try:
                since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
            except ValueError:
                since_dt = None
        level_map = {
            'info': {'INFO'},
            'warning': {'WARN', 'WARNING'},
            'error': {'ERROR'},
        }
        wanted_levels = level_map.get(level.lower()) if level else None
        entries: List[Dict[str, Any]] = []
        root = self.logs_root
        if root.exists():
            date_dirs = sorted([d for d in root.rglob('*') if d.is_dir() and d != root], reverse=True)
            if not date_dirs:
                date_dirs = [root]
            for d in date_dirs:
                for file in sorted(d.glob('*.log.jsonl'), reverse=True):
                    try:
                        with open(file, 'r') as f:
                            for line in f:
                                line = line.strip()
                                if not line:
                                    continue
                                try:
                                    obj = json.loads(line)
                                except json.JSONDecodeError:
                                    continue
                                ts_raw = obj.get('timestamp')
                                if not ts_raw:
                                    continue
                                try:
                                    ts_dt = datetime.fromisoformat(ts_raw.replace('Z', '+00:00'))
                                except ValueError:
                                    continue
                                if since_dt and ts_dt <= since_dt:
                                    continue
                                lvl = obj.get('level')
                                if wanted_levels and lvl not in wanted_levels:
                                    continue
                                entries.append({
                                    'ts': ts_dt.isoformat(),
                                    'level': 'info' if lvl == 'INFO' else 'warning' if lvl in ('WARN','WARNING') else 'error' if lvl == 'ERROR' else str(lvl).lower(),
                                    'message': obj.get('message'),
                                    'source': obj.get('component'),
                                    'context': obj.get('metadata') or {}
                                })
                    except (IOError, OSError):
                        continue
                if len(entries) >= limit * 2:
                    break
        entries.sort(key=lambda e: e['ts'], reverse=True)
        entries = entries[:limit]
        next_since = entries[-1]['ts'] if len(entries) == limit else None
        return {
            'entries': entries,
            'totalReturned': len(entries),
            'nextSince': next_since,
        }
