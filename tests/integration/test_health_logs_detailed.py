"""Detailed tests for /logs route creating synthetic log files.

These do not rely on the running container; they manipulate the expected log path.
"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import json

import pytest

from src.generators.health import HealthServer
from src.generators.lifecycle import GeneratorLifecycle
from src.generators.api import create_api_blueprint


@pytest.fixture()
def log_setup(tmp_path):
    # Create expected logs root: <repo_root>/data/manifests/logs/YYYY-MM-DD/
    repo_root = Path(__file__).parent.parent.parent
    logs_root = repo_root / "data" / "manifests" / "logs"
    base_now = datetime.now(timezone.utc)
    today_dir = logs_root / base_now.strftime("%Y-%m-%d")
    today_dir.mkdir(parents=True, exist_ok=True)

    # Stable timestamps relative to base_now for test comparisons
    entries = [
        {"timestamp": (base_now - timedelta(seconds=50)).isoformat(), "level": "INFO", "message": "Startup complete", "component": "orchestrator", "metadata": {"phase": "init"}},
        {"timestamp": (base_now - timedelta(seconds=40)).isoformat(), "level": "WARN", "message": "High memory usage", "component": "orchestrator", "metadata": {"mem_percent": 80}},
        {"timestamp": (base_now - timedelta(seconds=30)).isoformat(), "level": "ERROR", "message": "Batch failed", "component": "driver-generator", "metadata": {"batch_id": 12}},
        {"timestamp": (base_now - timedelta(seconds=20)).isoformat(), "level": "INFO", "message": "Recovery succeeded", "component": "driver-generator", "metadata": {"batch_id": 12}},
    ]
    log_file = today_dir / "orchestrator.log.jsonl"
    with open(log_file, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")

    yield logs_root, base_now

    # Cleanup
    for p in logs_root.glob("**/*"):
        if p.is_file():
            p.unlink()
    for p in sorted(logs_root.glob("**/*"), reverse=True):
        if p.is_dir():
            try:
                p.rmdir()
            except OSError:
                pass


@pytest.fixture()
def server():
    lifecycle = GeneratorLifecycle()
    srv = HealthServer(port=0, lifecycle=lifecycle)
    bp = create_api_blueprint(lifecycle, 'src/config/config.base.yaml', 'data/raw/companies.jsonl', 'data/raw/events', 'data/manifests/generator_state.json', 'data/manifests/logs')
    srv.app.register_blueprint(bp, url_prefix='/api')
    return srv


@pytest.fixture()
def client(server):
    return server.app.test_client()


def test_logs_level_filter(client, log_setup):
    logs_root, base_now = log_setup
    resp = client.get("/api/logs?level=error")
    assert resp.status_code == 200
    data = resp.get_json()
    assert all(e["level"] == "error" for e in data["entries"])
    assert data["totalReturned"] >= 1


def test_logs_since_filter(client, log_setup):
    logs_root, base_now = log_setup
    # Choose since timestamp older than oldest to ensure ascending filter semantics of implementation (which keeps only entries strictly after since)
    # Implementation keeps entries with ts > since. We pick the timestamp of second oldest entry so we expect the later two.
    second_oldest = (base_now - timedelta(seconds=40)).isoformat()
    since_ts = second_oldest
    from urllib.parse import quote
    encoded_since = quote(since_ts, safe="")
    resp = client.get(f"/api/logs?since={encoded_since}")
    assert resp.status_code == 200
    data = resp.get_json()
    # Compare using datetime objects for robustness
    from datetime import datetime
    since_dt = datetime.fromisoformat(since_ts.replace('Z', '+00:00'))
    returned_dts = [datetime.fromisoformat(e['ts'].replace('Z', '+00:00')) for e in data['entries']]
    # All returned entries should be strictly newer than since_dt (second oldest).
    assert all(d > since_dt for d in returned_dts), f"Found entries not newer than filter: {[d.isoformat() for d in returned_dts]} vs since {since_dt.isoformat()}"
    # Expect exactly the two most recent entries
    assert data["totalReturned"] == 2


def test_logs_limit(client, log_setup):
    logs_root, base_now = log_setup
    resp = client.get("/api/logs?limit=2")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["totalReturned"] == 2
    assert len(data["entries"]) == 2
    assert data["nextSince"] is not None


def test_logs_invalid_since(client, log_setup):
    logs_root, base_now = log_setup
    resp = client.get("/api/logs?since=not-a-date")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["totalReturned"] >= 1
