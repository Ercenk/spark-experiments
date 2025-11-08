import os
from pathlib import Path
from datetime import datetime, timezone

import pytest
from flask.testing import FlaskClient

from src.generators.health import HealthServer
from src.generators.lifecycle import GeneratorLifecycle


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
    return srv

@pytest.fixture
def client(server) -> FlaskClient:
    return server.app.test_client()


def test_auto_reinit_after_clean_and_resume(client, lifecycle, server, temp_data):
    # Ensure starting state: no companies, no events
    companies = server.companies_file
    events_dir = server.driver_events_dir
    assert not companies.exists()
    assert not events_dir.exists()

    # Invoke resume (while paused) should perform auto reinit
    resp = client.post('/resume')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['auto_reinit']['performed'] is True
    assert 'companies:' in data['auto_reinit']['actions'][0] or any(a.startswith('companies:') for a in data['auto_reinit']['actions'])
    assert any(a.startswith('driver_batch:') for a in data['auto_reinit']['actions'])

    # Files should now exist
    assert companies.exists() and companies.stat().st_size > 0
    assert events_dir.exists()
    # At least one batch subdirectory with events.jsonl
    batch_dirs = [p for p in events_dir.iterdir() if p.is_dir()]
    # Debug listing if missing
    if not batch_dirs:
        existing = list(events_dir.rglob('*'))
        pytest.fail(f"No batch dirs found in {events_dir}. Contents: {[str(e) for e in existing]}. Actions: {data['auto_reinit']['actions']}")
    assert any((d / 'events.jsonl').exists() for d in batch_dirs)

    # Health endpoint should reflect auto_reinit metadata
    lifecycle.pause()  # pause to stabilize status
    health = client.get('/health').get_json()
    assert health['auto_reinit']['performed'] is True
    assert health['auto_reinit']['at'] is not None
    assert isinstance(health['auto_reinit']['actions'], list)


def test_resume_without_missing_files_skips_reinit(client, lifecycle, server):
    # First resume triggers reinit
    first = client.post('/resume').get_json()
    assert first['auto_reinit']['performed'] is True

    # Pause again then resume; should not perform again
    lifecycle.pause()
    second = client.post('/resume').get_json()
    assert second['auto_reinit']['performed'] is True  # still true from first
    # Actions should be identical (no duplicate generation records) - we don't append on second resume
    assert second['auto_reinit']['at'] == first['auto_reinit']['at']
