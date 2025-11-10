import json
import pytest
from pathlib import Path
from datetime import datetime, timezone

from flask import Flask
from src.generators.lifecycle import GeneratorLifecycle
from src.generators.api import create_api_blueprint


@pytest.fixture
def app(tmp_path: Path):
    lifecycle = GeneratorLifecycle()
    cfg = tmp_path / "config.yaml"
    cfg.write_text("""
number_of_companies: 2
seed: 101
drivers_per_company: 3
event_rate_per_driver: 5
company_onboarding_interval: PT15M
driver_event_interval: PT15M
""")
    companies = tmp_path / "companies.jsonl"
    events = tmp_path / "events"
    state_file = tmp_path / "generator_state.json"
    logs_root = tmp_path / "logs"
    logs_root.mkdir()
    # minimal state file
    state_file.write_text(json.dumps({
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "lifecycle": {"paused": False},
        "last_company_batch": 0,
        "last_driver_batch": 0
    }))
    flask_app = Flask(__name__)
    bp = create_api_blueprint(
        lifecycle=lifecycle,
        config_path=str(cfg),
        companies_file=str(companies),
        events_dir=str(events),
        state_file=str(state_file),
        logs_root=str(logs_root),
    )
    flask_app.register_blueprint(bp, url_prefix="/api")
    return flask_app


def test_health_read_only(app):
    client = app.test_client()
    resp = client.get('/api/health')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'status' in data and data['status'] in {'running','paused'}
    assert 'verification' in data
    ver = data['verification']
    assert 'companies_exists' in ver
    assert 'events_exists' in ver


def test_resume_triggers_baseline(app):
    client = app.test_client()
    resp = client.post('/api/pause')
    assert resp.status_code == 200
    resp2 = client.post('/api/resume')
    assert resp2.status_code == 200
    data = resp2.get_json()
    assert data['status'] == 'running'
    assert 'extra' in data
    extra = data['extra']
    assert 'baseline_actions' in extra
    # Baseline actions should include companies or driver batch
    assert any('companies' in a for a in extra.get('baseline_actions', [])) or any('driver_batch' in a for a in extra.get('baseline_actions', []))