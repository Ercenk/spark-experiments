"""Health check endpoint for generator status monitoring."""

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List

from flask import Flask, jsonify, request
from pydantic import BaseModel, Field, field_validator
import yaml
import isodate

from datetime import timedelta


class UptimeModel(BaseModel):
    seconds: float
    hours: float
    start_time: str

class GeneratorStats(BaseModel):
    total_batches: int = Field(ge=0)
    last_batch_time: Optional[str] = None
    idle_seconds: Optional[float] = Field(default=None, ge=0)
    last_interval_end: Optional[str] = None  # only for driver

class LifecycleModel(BaseModel):
    paused: bool
    shutdown_requested: bool

class StateModel(BaseModel):
    last_saved: Optional[str]
    state_file: str

class AutoReinitModel(BaseModel):
    performed: bool = False
    at: Optional[str] = None
    actions: List[str] = []
    missing_files: List[str] = []

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    uptime: UptimeModel
    company_generator: GeneratorStats
    driver_generator: GeneratorStats
    lifecycle: LifecycleModel
    state: StateModel
    auto_reinit: AutoReinitModel

    @field_validator('status')
    def status_must_be_valid(cls, v):
        if v not in {'running', 'paused'}:
            raise ValueError('status must be running or paused')
        return v


class HealthServer:
    """Simple HTTP server for health checks and status monitoring including auto reinitialization."""
    
    def __init__(
        self,
        port: int = 8000,
        state_file: str = "data/manifests/generator_state.json",
        lifecycle=None,
        config_path: Optional[str] = None,
        companies_file: str = "data/raw/companies.jsonl",
        driver_events_dir: str = "data/raw/events"
    ):
        """
        Initialize health server.
        
        Args:
            port: HTTP port to listen on (default: 8000, mapped to 18000 externally)
            state_file: Path to generator state file
            lifecycle: Optional GeneratorLifecycle instance for pause/resume control
        """
        self.app = Flask(__name__)
        self.port = port
        self.state_file = Path(state_file)
        self.lifecycle = lifecycle
        self.start_time = datetime.now(timezone.utc)
        self.server_thread: Optional[threading.Thread] = None
        self.config_path = config_path
        self.companies_file = Path(companies_file)
        self.driver_events_dir = Path(driver_events_dir)
        self.auto_reinit_performed = False
        self.auto_reinit_time: Optional[str] = None
        self.auto_reinit_actions: List[str] = []
        self.auto_reinit_missing: List[str] = []
        
        # Root health endpoints removed; health served exclusively via /api/health blueprint.

        # CORS headers for SPA access from different host/port (e.g., Vite dev server)
        @self.app.after_request
        def add_cors_headers(resp):  # type: ignore
            resp.headers['Access-Control-Allow-Origin'] = '*'
            resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            return resp

        # Generic OPTIONS handler for CORS preflight
        @self.app.route('/<path:_any>', methods=['OPTIONS'])
        def cors_options(_any):  # type: ignore
            return ('', 204)

        @self.app.route('/', methods=['OPTIONS'])
        def cors_options_root():  # type: ignore
            return ('', 204)
    
    def _get_health_status(self):
        """Get current health and status information with comprehensive statistics."""
        current_time = datetime.now(timezone.utc)
        uptime_seconds = (current_time - self.start_time).total_seconds()
        
        # Load state from file
        state_data = {}
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state_data = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        lifecycle_state = state_data.get('lifecycle', {})
        # Override with live lifecycle object if available for real-time accuracy
        if self.lifecycle:
            lifecycle_state['paused'] = self.lifecycle.paused
            lifecycle_state['shutdown_requested'] = getattr(self.lifecycle, 'should_exit', False)
        
        # Calculate time since last activity
        last_company_time_str = state_data.get('last_company_time')
        last_driver_time_str = state_data.get('last_driver_time')
        
        company_idle_seconds = None
        driver_idle_seconds = None
        
        if last_company_time_str:
            try:
                last_company_time = datetime.fromisoformat(last_company_time_str.replace('Z', '+00:00'))
                company_idle_seconds = round((current_time - last_company_time).total_seconds(), 1)
            except (ValueError, AttributeError):
                pass
        
        if last_driver_time_str:
            try:
                last_driver_time = datetime.fromisoformat(last_driver_time_str.replace('Z', '+00:00'))
                driver_idle_seconds = round((current_time - last_driver_time).total_seconds(), 1)
            except (ValueError, AttributeError):
                pass
        
        # Build response with comprehensive statistics then validate via Pydantic
        raw_response = {
            "status": "paused" if lifecycle_state.get('paused', False) else "running",
            "timestamp": current_time.isoformat(),
            "uptime": {
                "seconds": round(uptime_seconds, 2),
                "hours": round(uptime_seconds / 3600, 2),
                "start_time": self.start_time.isoformat()
            },
            "company_generator": {
                "total_batches": int(state_data.get('last_company_batch', 0) or 0),
                "last_batch_time": last_company_time_str,
                "idle_seconds": company_idle_seconds
            },
            "driver_generator": {
                "total_batches": int(state_data.get('last_driver_batch', 0) or 0),
                "last_batch_time": last_driver_time_str,
                "last_interval_end": state_data.get('last_interval_end'),
                "idle_seconds": driver_idle_seconds
            },
            "lifecycle": {
                "paused": bool(lifecycle_state.get('paused', False)),
                "shutdown_requested": bool(lifecycle_state.get('shutdown_requested', False))
            },
            "state": {
                "last_saved": state_data.get('saved_at'),
                "state_file": str(self.state_file)
            },
            "auto_reinit": {
                "performed": self.auto_reinit_performed,
                "at": self.auto_reinit_time,
                "actions": self.auto_reinit_actions,
                "missing_files": self.auto_reinit_missing
            }
        }

        validated = HealthResponse(**raw_response)
        return jsonify(validated.model_dump())
    
    # Legacy mutation methods removed with deprecation cleanup
    
    def _clean_data(self):
        """Clean all generated data files via REST API."""
        import shutil
        
        # Check if generator is running
        if self.lifecycle and not self.lifecycle.paused:
            return jsonify({
                "success": False,
                "error": "Generator must be paused before cleaning data",
                "message": "Send POST to /pause first"
            }), 400
        
        base_dir = Path(__file__).parent.parent.parent
        data_dir = base_dir / "data"
        
        # Define paths to clean
        paths_to_clean = {
            "companies_file": data_dir / "raw" / "companies.jsonl",
            "event_batches": data_dir / "raw" / "events",
            "seed_manifest": data_dir / "manifests" / "seed_manifest.json",
            "batch_manifest": data_dir / "manifests" / "batch_manifest.json",
            "generator_state": data_dir / "manifests" / "generator_state.json",
            "dataset_descriptor": data_dir / "manifests" / "dataset.md",
            "logs": data_dir / "manifests" / "logs",
        }
        
        # Track what was deleted
        deleted = []
        errors = []
        
        for name, path in paths_to_clean.items():
            if not path.exists():
                continue
            
            try:
                if path.is_file():
                    size = path.stat().st_size
                    path.unlink()
                    deleted.append({
                        "name": name,
                        "path": str(path),
                        "type": "file",
                        "size": size
                    })
                elif path.is_dir():
                    files = list(path.rglob("*"))
                    file_count = len([f for f in files if f.is_file()])
                    shutil.rmtree(path)
                    deleted.append({
                        "name": name,
                        "path": str(path),
                        "type": "directory",
                        "file_count": file_count
                    })
            except Exception as e:
                errors.append({
                    "name": name,
                    "path": str(path),
                    "error": str(e)
                })
        
        # Ensure directories exist
        (data_dir / "raw").mkdir(parents=True, exist_ok=True)
        (data_dir / "manifests").mkdir(parents=True, exist_ok=True)
        (data_dir / "staged").mkdir(parents=True, exist_ok=True)
        (data_dir / "processed").mkdir(parents=True, exist_ok=True)
        
        # Reset auto reinit flags so next resume can run baseline generation
        self.auto_reinit_performed = False
        self.auto_reinit_time = None
        self.auto_reinit_actions = []
        self.auto_reinit_missing = []

        response = {
            "success": len(errors) == 0,
            "deleted_count": len(deleted),
            "deleted_items": deleted,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if errors:
            response["errors"] = errors
            response["message"] = f"Cleanup completed with {len(errors)} errors"
        else:
            response["message"] = "All data cleaned successfully. Restart generator container to reinitialize."
        
        return jsonify(response), 200 if len(errors) == 0 else 207

    def _get_logs(self):
        """Return recent log entries with optional filtering.

        Query Params:
            limit: int (default 100)
            since: ISO8601 timestamp (only entries after this)
            level: info|warning|error (case-insensitive)
        Response:
            {
              "entries": [ { ts, level, message, source, context } ],
              "totalReturned": n,
              "nextSince": oldest_ts_or_null
            }
        """
        limit_param = request.args.get('limit', '100')
        since_param = request.args.get('since')
        level_param = request.args.get('level')

        try:
            limit = max(1, min(1000, int(limit_param)))
        except ValueError:
            limit = 100

        since_dt = None
        if since_param:
            try:
                since_dt = datetime.fromisoformat(since_param.replace('Z', '+00:00'))
            except ValueError:
                since_dt = None

        level_map = {
            'info': {'INFO'},
            'warning': {'WARN', 'WARNING'},
            'error': {'ERROR'}
        }
        wanted_levels = None
        if level_param:
            key = level_param.lower()
            wanted_levels = level_map.get(key)
            if not wanted_levels:
                wanted_levels = None

        base_dir = Path(__file__).parent.parent.parent
        logs_root = base_dir / 'data' / 'manifests' / 'logs'
        entries = []

        if logs_root.exists():
            # Choose most recent date directories first
            date_dirs = sorted([d for d in logs_root.rglob('*') if d.is_dir() and d != logs_root], reverse=True)
            # If empty, maybe logs stored directly
            if not date_dirs:
                date_dirs = [logs_root]

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
                                level_raw = obj.get('level')
                                if wanted_levels and level_raw not in wanted_levels:
                                    continue
                                entries.append({
                                    'ts': ts_dt.isoformat(),
                                    'level': 'info' if level_raw == 'INFO' else 'warning' if level_raw in ('WARN','WARNING') else 'error' if level_raw == 'ERROR' else level_raw.lower(),
                                    'message': obj.get('message'),
                                    'source': obj.get('component'),
                                    'context': obj.get('metadata') or {}
                                })
                    except (IOError, OSError):
                        continue
                # Stop early if enough entries gathered
                if len(entries) >= limit * 2:  # gather some slack before final sort
                    break

        # Sort descending by timestamp
        entries.sort(key=lambda e: e['ts'], reverse=True)
        entries = entries[:limit]
        next_since = entries[-1]['ts'] if len(entries) == limit else None

        return jsonify({
            'entries': entries,
            'totalReturned': len(entries),
            'nextSince': next_since
        })
    
    def start_background(self):
        """Start health server in background thread."""
        def run_server():
            self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
    
    def start(self):
        """Start health server (blocking)."""
        self.app.run(host='0.0.0.0', port=self.port, debug=False)
