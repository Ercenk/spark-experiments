import json
from pathlib import Path
from typing import Set

from .constants import PROCESSED_FILES_MANIFEST

class FileTracker:
    def __init__(self, manifest_path: str = PROCESSED_FILES_MANIFEST):
        self.manifest_path = Path(manifest_path)
        self._loaded: Set[str] = set()
        self._load()

    def _load(self):
        if self.manifest_path.exists():
            try:
                self._loaded = set(json.loads(self.manifest_path.read_text()))
            except Exception:
                self._loaded = set()
        else:
            self._loaded = set()

    def is_processed(self, filename: str) -> bool:
        return filename in self._loaded

    def mark_processed(self, filename: str):
        self._loaded.add(filename)

    def save(self):
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.manifest_path.write_text(json.dumps(sorted(self._loaded), indent=2))
