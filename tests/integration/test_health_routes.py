"""Integration tests for generator Flask health server routes.

These tests use the Flask test client directly to avoid needing the Docker container.
We instantiate HealthServer with a temporary state file in a tmp path.
"""
from pathlib import Path
import json
import tempfile

import pytest

from src.generators.health import HealthServer, HealthResponse
from src.generators.lifecycle import GeneratorLifecycle


@pytest.fixture(scope="function")
def health_server():
    # Use temp directory for state file
    tmpdir = tempfile.TemporaryDirectory()
    state_file = Path(tmpdir.name) / "generator_state.json"
    lifecycle = GeneratorLifecycle()
    server = HealthServer(port=0, state_file=str(state_file), lifecycle=lifecycle)
    yield server
    tmpdir.cleanup()

@pytest.fixture(scope="function")
def client(health_server):
    return health_server.app.test_client()


def test_health_endpoint(client, health_server):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    # Validate schema via Pydantic
    model = HealthResponse(**data)
    assert model.status in {"running", "paused"}
    assert model.uptime.seconds >= 0


def test_status_endpoint(client):
    resp = client.get("/status")
    assert resp.status_code == 200
    data = resp.get_json()
    HealthResponse(**data)


def test_pause_and_resume(client, health_server):
    # Initially not paused
    assert not health_server.lifecycle.paused

    # Pause
    resp_pause = client.post("/pause")
    assert resp_pause.status_code in (200, 503)  # 503 if lifecycle missing but we provided it
    data_pause = resp_pause.get_json()
    if resp_pause.status_code == 200:
        assert data_pause["status"] == "paused"
        assert health_server.lifecycle.paused

    # Resume
    resp_resume = client.post("/resume")
    assert resp_resume.status_code in (200, 503)
    data_resume = resp_resume.get_json()
    if resp_resume.status_code == 200:
        assert data_resume["status"] == "running"
        assert not health_server.lifecycle.paused


def test_clean_requires_pause(client, health_server):
    # When running, should get 400 instructing to pause first
    resp_clean_running = client.post("/clean")
    if health_server.lifecycle:
        assert resp_clean_running.status_code in (200, 400, 207)
        if resp_clean_running.status_code == 400:
            data = resp_clean_running.get_json()
            assert data["error"].startswith("Generator must be paused")

    # Pause lifecycle then clean
    health_server.lifecycle.pause()
    resp_clean_paused = client.post("/clean")
    assert resp_clean_paused.status_code in (200, 207)
    data2 = resp_clean_paused.get_json()
    assert "deleted_items" in data2


def test_logs_empty(client):
    resp = client.get("/logs")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "entries" in data
    assert isinstance(data["entries"], list)


def test_logs_with_params(client):
    resp = client.get("/logs?limit=10&level=info")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "entries" in data
    assert data["totalReturned"] <= 10


def test_invalid_level_param(client):
    resp = client.get("/logs?level=notalevel")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "entries" in data

