"""JSON logging utilities for structured event logging."""

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class JSONLogger:
    """
    Structured JSON logger for generator events.
    
    Emits JSON Lines format with standard fields:
    - timestamp: ISO8601 UTC
    - component: Logger name/component identifier
    - run_id: UUID for this execution
    - level: INFO/WARN/ERROR
    - message: Human-readable message
    - metadata: Additional structured data
    
    Logs are always written to stdout for container visibility.
    If log_file is provided, logs are also persisted to disk.
    """
    
    def __init__(self, component: str, run_id: Optional[str] = None, log_file: Optional[str] = None):
        """
        Initialize JSON logger.
        
        Args:
            component: Component name for log entries
            run_id: Optional run UUID; generated if not provided
            log_file: Optional file path for log output; always logs to stdout, also logs to file if provided
        """
        self.component = component
        self.run_id = run_id or str(uuid.uuid4())
        self.log_file = Path(log_file) if log_file else None
        
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _write_log(self, level: str, message: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Write structured log entry to stdout and optionally to file."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "component": self.component,
            "run_id": self.run_id,
            "level": level,
            "message": message,
            "metadata": metadata or {}
        }
        
        log_line = json.dumps(entry)
        
        # Always write to stdout for container visibility
        print(log_line, flush=True)
        
        # Also write to file if configured
        if self.log_file:
            with open(self.log_file, 'a') as f:
                f.write(log_line + '\n')
    
    def info(self, message: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Log INFO level message."""
        self._write_log("INFO", message, metadata)
    
    def warn(self, message: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Log WARN level message."""
        self._write_log("WARN", message, metadata)
    
    def error(self, message: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Log ERROR level message."""
        self._write_log("ERROR", message, metadata)
