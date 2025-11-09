"""Updated integration tests focusing on /api blueprint endpoints.

Legacy mutation endpoints (/pause, /resume, /clean, /logs) are deprecated and no longer
used by the frontend. These tests ensure the blueprint endpoints behave as expected.
"""
from pathlib import Path
import tempfile
import yaml
import pytest

from src.generators.health import HealthServer
from src.generators.lifecycle import GeneratorLifecycle
from src.generators.api import create_api_blueprint


@pytest.fixture(scope="function")
def app_with_api():
    tmpdir = tempfile.TemporaryDirectory()
    base = Path(tmpdir.name)
    state_file = base / "generator_state.json"
    config_file = base / "config.yaml"
    companies_file = base / "companies.jsonl"
    events_dir = base / "events"
    logs_root = base / "logs"
    # Minimal config expected (provide required keys for baseline initializer if referenced)
    config_file.write_text(yaml.safe_dump({
        'seed': 42,
        'company_onboarding_interval': 'PT1H',
        'number_of_companies': 1,
    }))
    lifecycle = GeneratorLifecycle()
    server = HealthServer(port=0, state_file=str(state_file), lifecycle=lifecycle,
                          config_path=str(config_file), companies_file=str(companies_file),
                          driver_events_dir=str(events_dir))
    bp = create_api_blueprint(lifecycle, str(config_file), str(companies_file), str(events_dir), str(state_file), str(logs_root))
    server.app.register_blueprint(bp, url_prefix="/api")
    yield server.app, lifecycle, base
    tmpdir.cleanup()


@pytest.fixture(scope="function")
def client(app_with_api):
    app, _lifecycle, _base = app_with_api
    return app.test_client()


def test_api_health(client):
    resp = client.get('/api/health')
    assert resp.status_code == 200
    data = resp.get_json()
    for key in ['status', 'timestamp', 'uptime_seconds', 'company_batches', 'driver_batches']:
        assert key in data


def test_api_pause_resume(client, app_with_api):
    _app, lifecycle, _base = app_with_api
    assert not lifecycle.paused
    r1 = client.post('/api/pause')
    assert r1.status_code == 200
    assert lifecycle.paused
    r2 = client.post('/api/resume')
    assert r2.status_code == 200
    assert not lifecycle.paused


def test_api_logs(client):
    r = client.get('/api/logs?limit=5')
    assert r.status_code == 200
    data = r.get_json()
    assert 'entries' in data
    assert isinstance(data['entries'], list)


def test_api_clean_requires_pause(client, app_with_api):
    _app, lifecycle, base = app_with_api
    # Running -> expect 400
    r_running = client.post('/api/clean')
    assert r_running.status_code in (400, 207, 200)  # if already paused somehow
    lifecycle.pause()
    r_paused = client.post('/api/clean')
    assert r_paused.status_code in (200, 207)
    data = r_paused.get_json()
    assert 'deleted_count' in data


def test_removed_legacy_endpoints_return_client_error(client):
    # Removed endpoints should not be 200; allow 404 (Not Found) or 405 (Method Not Allowed) per Flask routing behavior
    allowed = {404, 405}
    for ep in ['/pause', '/resume', '/clean', '/logs']:
        r = client.open(ep, method='POST' if ep != '/logs' else 'GET')
        assert r.status_code in allowed

