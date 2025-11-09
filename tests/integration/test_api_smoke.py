"""Smoke tests for /api endpoints to ensure stable contract used by frontend."""
from pathlib import Path
import tempfile
import yaml
import pytest

from src.generators.health import HealthServer
from src.generators.lifecycle import GeneratorLifecycle
from src.generators.api import create_api_blueprint


@pytest.fixture(scope="function")
def api_client():
    tmpdir = tempfile.TemporaryDirectory()
    base = Path(tmpdir.name)
    state_file = base / "generator_state.json"
    config_file = base / "config.yaml"
    companies_file = base / "companies.jsonl"
    events_dir = base / "events"
    logs_root = base / "logs"
    config_file.write_text(yaml.safe_dump({
        'seed': 1,
        'company_onboarding_interval': 'PT30M',
        'number_of_companies': 1,
    }))
    lifecycle = GeneratorLifecycle()
    server = HealthServer(port=0, state_file=str(state_file), lifecycle=lifecycle,
                          config_path=str(config_file), companies_file=str(companies_file),
                          driver_events_dir=str(events_dir))
    bp = create_api_blueprint(lifecycle, str(config_file), str(companies_file), str(events_dir), str(state_file), str(logs_root))
    server.app.register_blueprint(bp, url_prefix='/api')
    client = server.app.test_client()
    try:
        yield client, lifecycle
    finally:
        tmpdir.cleanup()


def test_smoke_health(api_client):
    client, _ = api_client
    r = client.get('/api/health')
    assert r.status_code == 200
    data = r.get_json()
    assert data['status'] in ('running', 'paused')
    assert 'uptime_seconds' in data


def test_smoke_pause_resume(api_client):
    client, lifecycle = api_client
    assert not lifecycle.paused
    rp = client.post('/api/pause')
    assert rp.status_code == 200
    assert lifecycle.paused
    rr = client.post('/api/resume')
    assert rr.status_code == 200
    assert not lifecycle.paused


def test_smoke_logs(api_client):
    client, _ = api_client
    rl = client.get('/api/logs?limit=2')
    assert rl.status_code == 200
    data = rl.get_json()
    assert 'entries' in data
    assert isinstance(data['entries'], list)


def test_smoke_clean(api_client):
    client, lifecycle = api_client
    lifecycle.pause()
    rc = client.post('/api/clean')
    assert rc.status_code in (200, 207)
    data = rc.get_json()
    assert 'deleted_count' in data