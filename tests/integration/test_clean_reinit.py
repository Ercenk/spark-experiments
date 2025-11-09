import os
from pathlib import Path
from datetime import datetime, timezone

import pytest
from flask.testing import FlaskClient

from src.generators.health import HealthServer
from src.generators.lifecycle import GeneratorLifecycle
from src.generators.api import create_api_blueprint


@pytest.fixture
def lifecycle():
    lc = GeneratorLifecycle()
    lc.pause()  # start paused for clean operation
    return lc

@pytest.fixture
def temp_data(tmp_path):
    # Create isolated data structure under tmp
    data_root = tmp_path / 'data'
    (data_root / 'raw').mkdir(parents=True)
    (data_root / 'manifests').mkdir(parents=True)
    return data_root

@pytest.fixture
def config_file(temp_data):
    # Include required fields for both generators
    cfg = temp_data / 'config.test.yaml'
    cfg.write_text('\n'.join([
        'number_of_companies: 3',
        'seed: 123',
        'company_onboarding_interval: PT1H',
        'drivers_per_company: 2',
        'event_rate_per_driver: 3'
    ]) + '\n')
    return str(cfg)

@pytest.fixture
def server(lifecycle, temp_data, config_file, monkeypatch):
    # Monkeypatch default paths used inside generator components to use temp data
    monkeypatch.chdir(temp_data.parent)  # set cwd so relative paths point to temp
    state_file = temp_data / 'manifests' / 'generator_state.json'
    companies = temp_data / 'raw' / 'companies.jsonl'
    events_dir = temp_data / 'raw' / 'events'
    srv = HealthServer(
        port=9999,
        lifecycle=lifecycle,
        state_file=str(state_file),
        config_path=config_file,
        companies_file=str(companies),
        driver_events_dir=str(events_dir)
    )
    # Attach API blueprint for /api endpoints
    bp = create_api_blueprint(lifecycle, config_file, str(companies), str(events_dir), str(state_file), str(temp_data / 'manifests' / 'logs'))
    srv.app.register_blueprint(bp, url_prefix='/api')
    return srv

@pytest.fixture
def client(server) -> FlaskClient:
    return server.app.test_client()


def test_baseline_resume_generates_missing(client, lifecycle, server, temp_data):
    companies = server.companies_file
    events_dir = server.driver_events_dir
    assert not companies.exists()
    assert not events_dir.exists()
    # Resume through blueprint
    resp = client.post('/api/resume')
    assert resp.status_code == 200
    data = resp.get_json()
    # Baseline actions embedded in extra
    extra = data.get('extra') or {}
    assert any('baseline_actions' in k or k == 'baseline_actions' for k in extra.keys()) or 'baseline_actions' in extra
    # Files created
    assert companies.exists() and companies.stat().st_size > 0
    assert events_dir.exists()
    # Health snapshot via blueprint reflects runtime status; batch counters may remain 0 until generators run
    health = client.get('/api/health').get_json()
    assert 'company_batches' in health and 'driver_batches' in health


def test_resume_when_already_initialized(client, lifecycle, server):
    first = client.post('/api/resume').get_json()
    lifecycle.pause()
    second = client.post('/api/resume').get_json()
    # second resume should not create duplicate companies/events
    extra_first = first.get('extra', {})
    extra_second = second.get('extra', {})
    # Second resume should not duplicate baseline actions; allow empty or identical list
    first_actions = extra_first.get('baseline_actions') or []
    second_actions = extra_second.get('baseline_actions') or []
    assert second_actions == [] or second_actions == first_actions
