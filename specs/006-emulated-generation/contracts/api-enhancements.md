# API Contracts: Emulated Fast-Cadence Data Generation

**Feature**: 006-emulated-generation  
**Created**: 2025-11-09  
**Status**: Design

## Overview

This feature **does not introduce new HTTP endpoints**. Emulated mode is controlled via configuration files, not API calls. However, existing API responses are enhanced to include mode indicators for observability.

## Enhanced Existing Endpoints

### GET /api/health

**Purpose**: Aggregated health snapshot (existing endpoint)

**Changes**: Add `generation_mode` field to response

**Request**: No changes

**Response** (enhanced):

```json
{
  "status": "running|paused",
  "timestamp": "2025-11-09T12:34:56.789Z",
  "generation_mode": "emulated",  // NEW: "production" or "emulated"
  "uptime": {
    "seconds": 123.45,
    "hours": 0.034,
    "start_time": "2025-11-09T12:30:00.000Z"
  },
  "company_generator": {
    "total_batches": 24,  // Higher in emulated mode (10s vs 1h intervals)
    "last_batch_time": "2025-11-09T12:34:50.000Z",
    "idle_seconds": 6.5
  },
  "driver_generator": {
    "total_batches": 24,  // Higher in emulated mode (10s vs 15min intervals)
    "last_batch_time": "2025-11-09T12:34:50.000Z",
    "last_interval_end": "2025-11-09T12:35:00.000Z",
    "idle_seconds": 6.5
  },
  "lifecycle": {
    "paused": false,
    "shutdown_requested": false
  },
  "state": {
    "last_saved": "2025-11-09T12:34:50.000Z",
    "state_file": "data/manifests/generator_state.json"
  },
  "emulated_config": {  // NEW: Only present when mode=emulated
    "company_interval_seconds": 10,
    "driver_interval_seconds": 10,
    "companies_per_batch": 10,
    "events_per_batch_range": [5, 20]
  }
}
```

**Schema Changes**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `generation_mode` | `string` | Yes | Enum: `"production"`, `"emulated"` |
| `emulated_config` | `object` | No | Only present when `generation_mode="emulated"` |
| `emulated_config.company_interval_seconds` | `number` | Conditional | Company batch interval in seconds |
| `emulated_config.driver_interval_seconds` | `number` | Conditional | Driver batch interval in seconds |
| `emulated_config.companies_per_batch` | `number` | Conditional | Configured company count per batch |
| `emulated_config.events_per_batch_range` | `array[number]` | Conditional | `[min, max]` event count range |

**Backward Compatibility**: Existing clients ignore unknown fields; no breaking changes.

---

### GET /api/logs

**Purpose**: Retrieve structured log entries (existing endpoint)

**Changes**: Log entries include mode indicator in emulated batches

**Request**: No changes (query params `limit`, `since`, `level` unchanged)

**Response**: No schema changes; log entries naturally include mode info via `message` field

**Example Log Entry** (emulated mode):

```json
{
  "timestamp": "2025-11-09T12:34:56.789Z",
  "level": "INFO",
  "logger": "company_generator",
  "message": "Generated batch 24 (emulated mode): 10 companies, 6 corrupted",
  "extra": {
    "batch_id": "20241109T123450Z",
    "mode": "emulated",  // NEW field in extra context
    "valid_count": 4,
    "corrupted_count": 6,
    "interval_seconds": 10
  }
}
```

**Schema Changes**: None (existing `extra` field accommodates arbitrary metadata)

---

## Configuration File Format

While not HTTP API, configuration is the primary interface for enabling emulated mode.

### Configuration Schema

**File**: `src/config/config.emulated.yaml`

**Format**: YAML (validated against Pydantic `Config` model)

**Example**:

```yaml
# Base generator configuration (production values)
seed: 42
number_of_companies: 100
drivers_per_company: 10
event_rate_per_driver: 3.5
company_onboarding_interval: PT1H   # Production: hourly
driver_event_interval: PT15M        # Production: 15 minutes

# Quality injection (reused from feature 005)
quality_injection:
  enabled: true
  corruption_rate: 0.3

# Emulated mode configuration
emulated_mode:
  enabled: true                     # Toggle emulated mode
  company_batch_interval: PT10S     # Override: 10 seconds
  driver_batch_interval: PT10S      # Override: 10 seconds
  companies_per_batch: 10           # Override: 10 companies
  events_per_batch_min: 5           # Override: 5-20 events
  events_per_batch_max: 20
```

**Validation Rules** (enforced by Pydantic):

| Rule | Constraint | Error Message |
|------|------------|---------------|
| Interval format | ISO 8601 duration `^PT(\d+H)?(\d+M)?(\d+S)?$` | `"Invalid ISO8601 duration: {value}"` |
| Interval minimum | ≥1 second | `"Emulated interval must be >= 1 second, got {value}"` |
| Batch size minimum | `companies_per_batch >= 1` | `"Value must be >= 1"` |
| Batch size maximum | `companies_per_batch <= 100` | `"Value must be <= 100"` |
| Event range order | `events_per_batch_max >= events_per_batch_min` | `"Max must be >= min"` |

---

## Internal State Updates

While not exposed via HTTP, internal state files are enhanced for mode awareness.

### generator_state.json

**Changes**: Add `generation_mode` field

```json
{
  "generation_mode": "emulated",  // NEW
  "company_generator": {
    "total_batches": 24,
    "last_batch_time": "2025-11-09T12:34:50.000Z",
    "last_batch_counter": 24
  },
  "driver_generator": {
    "total_batches": 24,
    "last_batch_time": "2025-11-09T12:34:50.000Z",
    "last_batch_counter": 24,
    "last_interval_end": "2025-11-09T12:35:00.000Z"
  },
  "last_saved": "2025-11-09T12:34:50.000Z"
}
```

---

## Dashboard Integration (Future)

**Note**: This section describes **future enhancements** if dashboard implements real-time updates (User Story 3).

### WebSocket Event Stream (Proposed)

**Endpoint**: `ws://localhost:18000/api/stream` (not implemented yet)

**Purpose**: Push batch events to dashboard for real-time visualization

**Event Format**:

```json
{
  "event": "batch_generated",
  "timestamp": "2025-11-09T12:34:56.789Z",
  "mode": "emulated",
  "generator": "company",
  "batch_id": "20241109T123450Z",
  "record_count": 10,
  "corrupted_count": 6,
  "interval_seconds": 10
}
```

**Client Usage** (pseudocode):

```javascript
const ws = new WebSocket('ws://localhost:18000/api/stream');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.event === 'batch_generated') {
    updateDashboardMetrics(data);
  }
};
```

---

## Error Responses (No Changes)

Existing error response format unchanged:

```json
{
  "error": "string",
  "detail": "string",
  "timestamp": "ISO8601"
}
```

**Example** (invalid config):

```bash
# Start generator with invalid emulated interval
docker compose up generator

# Logs contain Pydantic validation error
{
  "timestamp": "2025-11-09T12:00:00.000Z",
  "level": "ERROR",
  "message": "Config validation failed",
  "error": "Emulated interval must be >= 1 second, got 0:00:00.500000"
}
```

---

## Contract Testing

Validation tests for enhanced endpoints:

### Health Endpoint Contract Test

```python
# tests/contract/test_api_health_emulated.py
import pytest
from src.generators.api import create_app
from src.generators.config import Config

def test_health_endpoint_emulated_mode():
    """Verify /api/health includes emulated mode indicators."""
    config = Config.from_yaml("src/config/config.emulated.yaml")
    assert config.emulated_mode.enabled
    
    app = create_app(config)
    client = app.test_client()
    
    response = client.get('/api/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['generation_mode'] == 'emulated'
    assert 'emulated_config' in data
    assert data['emulated_config']['company_interval_seconds'] == 10
    assert data['emulated_config']['driver_interval_seconds'] == 10

def test_health_endpoint_production_mode():
    """Verify /api/health handles production mode correctly."""
    config = Config.from_yaml("src/config/config.base.yaml")
    assert not config.emulated_mode.enabled
    
    app = create_app(config)
    client = app.test_client()
    
    response = client.get('/api/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['generation_mode'] == 'production'
    assert 'emulated_config' not in data  # Not present in production mode
```

---

## Assumptions

1. **No New Endpoints**: Emulated mode is configuration-driven, not API-driven
2. **Backward Compatibility**: Existing API clients ignore new fields (additive changes only)
3. **Dashboard Polling**: If dashboard exists, it polls `/api/health` more frequently (e.g., every 2 seconds) when detecting emulated mode
4. **WebSocket Future**: Real-time streaming deferred to future enhancement (not required for MVP)

## References

- [Existing API Blueprint](../../src/generators/api/__init__.py): Flask route definitions
- [Health Response Schema](../../tests/contract/test_api_blueprint_health.py): Current contract tests
- [Config Model](../../src/generators/config.py): Pydantic validation logic
