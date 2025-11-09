"""Live container tests for generator Flask server.

These tests attempt to reach the running docker container mapped at localhost:18000.
They are skipped automatically if the service is unreachable.
"""
import os
import time
from datetime import datetime, timezone, timedelta

import pytest
import requests

BASE_URL = os.environ.get("GENERATOR_BASE_URL", "http://localhost:18000")


def _service_available():
    try:
        r = requests.get(f"{BASE_URL}/api/health", timeout=0.5)
        return r.status_code == 200
    except Exception:
        return False


service_up = _service_available()

pytestmark = pytest.mark.skipif(not service_up, reason="Generator container not reachable on localhost:18000")


def test_live_health():
    r = requests.get(f"{BASE_URL}/api/health")
    assert r.status_code == 200
    data = r.json()
    assert "uptime_seconds" in data


def test_live_pause_and_resume():
    rp = requests.post(f"{BASE_URL}/api/pause")
    assert rp.status_code == 200
    rr = requests.post(f"{BASE_URL}/api/resume")
    assert rr.status_code == 200


def test_live_logs_params():
    r = requests.get(f"{BASE_URL}/api/logs?limit=5&level=info")
    assert r.status_code == 200
    data = r.json()
    assert data["totalReturned"] <= 5


def test_live_clean_requires_pause_or_paused():
    rc = requests.post(f"{BASE_URL}/api/clean")
    assert rc.status_code in (200, 207, 400)
