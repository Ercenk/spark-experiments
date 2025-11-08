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
        r = requests.get(f"{BASE_URL}/health", timeout=0.5)
        return r.status_code == 200
    except Exception:
        return False


service_up = _service_available()

pytestmark = pytest.mark.skipif(not service_up, reason="Generator container not reachable on localhost:18000")


def test_live_health():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    data = r.json()
    assert "uptime" in data


def test_live_pause_and_resume():
    # Pause
    rp = requests.post(f"{BASE_URL}/pause")
    assert rp.status_code in (200, 503)
    # Resume
    rr = requests.post(f"{BASE_URL}/resume")
    assert rr.status_code in (200, 503)


def test_live_logs_params():
    r = requests.get(f"{BASE_URL}/logs?limit=5&level=info")
    assert r.status_code == 200
    data = r.json()
    assert data["totalReturned"] <= 5


def test_live_clean_requires_pause_or_paused():
    # Try clean (may 400 if not paused)
    rc = requests.post(f"{BASE_URL}/clean")
    assert rc.status_code in (200, 207, 400)
