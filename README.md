# Spark Experiments: Driving Batch Generators

**Purpose**: Learn Apache Spark through reproducible local experimentation with synthetic driving event data.

## Overview

This project generates synthetic data simulating:
- Company onboarding records (transportation companies)
- Driver event batches every 15 minutes (start driving, stopped driving, delivered)

Features:
- **Reproducible**: Seeded random generation ensures identical output
- **Local-first**: Multi-container Docker Compose environment (Spark + Python generators)
- **Configurable**: YAML configs for company count, driver density, event rates
- **Realistic randomness**: Poisson inter-arrival for event counts, weighted categorical sampling for event types

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development/testing)

### 1. Launch Environment (Continuous Mode)

```powershell
cd docker
docker compose up -d
```

This starts:
- `spark-driver`: Spark master (apache/spark:3.5.0, port 17080)
- `spark-executor`: Spark worker
- `generator`: **Automatically generates data continuously** (port 18000 for health checks)

**The generator container now runs continuously**, generating:
- Company onboarding batches at configured intervals (default: hourly)
- Driver event batches every 15 minutes

### 2. Runtime Control via HTTP

Current REST surface is served exclusively under the mounted API blueprint prefix:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Aggregated health snapshot (status, uptime, batch counters) |
| `/api/pause` | POST | Pause continuous generation (idempotent) |
| `/api/resume` | POST | Resume generation; performs baseline initialization if missing |
| `/api/clean` | POST | Delete generated data (requires paused) |
| `/api/logs` | GET | Structured log entries with query params `limit`, `since`, `level` |

All root endpoints (`/health`, `/status`, `/pause`, `/resume`, `/clean`, `/logs`) have been **removed**. Use only `/api/*` paths.

PowerShell / curl examples (new API):

```powershell
# Recommended: install native jq (winget install jqlang.jq or choco install jq -y)

# Health / status (preferred new endpoint)
curl.exe -s http://localhost:18000/api/health | jq .status

# Pause and resume
curl.exe -s -X POST http://localhost:18000/api/pause | jq .status
curl.exe -s -X POST http://localhost:18000/api/resume | jq '.extra.baseline_actions'

# Clean data (must be paused first)
curl.exe -s -X POST http://localhost:18000/api/pause > $null
curl.exe -s -X POST http://localhost:18000/api/clean | jq '.deleted_count'
curl.exe -s -X POST http://localhost:18000/api/resume > $null

# Logs (limit + level + since)
curl.exe -s "http://localhost:18000/api/logs?limit=5" | jq '.entries[] | {ts,level,message}'
curl.exe -s "http://localhost:18000/api/logs?limit=10&level=error" | jq '.totalReturned'
$since = (curl.exe -s "http://localhost:18000/api/logs?limit=5" | jq -r .nextSince)
curl.exe -s "http://localhost:18000/api/logs?since=$( [uri]::EscapeDataString($since) )&limit=5" | jq '.entries | length'

# PowerShell fallback (no jq):
(Invoke-WebRequest http://localhost:18000/api/health).Content | ConvertFrom-Json | Select-Object -ExpandProperty status
```

### 3. Monitor Generation

```powershell
# View live logs
docker compose logs -f generator

# Check generated files
docker compose exec generator sh -c "ls -lh /data/raw/companies.jsonl"
docker compose exec generator sh -c "ls -lh /data/raw/events/"

# View state
docker compose exec generator sh -c "cat /data/manifests/generator_state.json"
```

### 4. Manual Single-Batch Generation (Alternative)

If you prefer manual control instead of continuous mode:

```powershell
# Stop continuous generator
docker compose down

# Run company generator once
docker compose run generator python -m src.generators.company_generator `
  --config /app/src/config/config.base.yaml `
  --output /data/raw/companies.jsonl

# Run driver generator once
docker compose run generator python -m src.generators.driver_event_generator `
  --config /app/src/config/config.base.yaml `
  --output /data/raw/events `
  --companies /data/raw/companies.jsonl `
  --now
```

### Teardown

```powershell
docker compose down      # Stop containers, keep data
docker compose down -v   # Warning: removes all data volumes
```

## Configuration Presets

| Config | Companies | Drivers/Co | Event Rate | Use Case |
|--------|-----------|------------|------------|----------|
| `config.small.yaml` | 5 | 5 | 2.0 | Quick testing |
| `config.base.yaml` | 100 | 10 | 3.5 | Baseline experiments |
| `config.scaling.yaml` | 1000 | 20 | 5.0 | Performance testing |

## Project Structure

```
src/
├── generators/          # Python data generators
│   ├── company_generator.py
│   ├── driver_event_generator.py
│   ├── config.py        # Pydantic validation
│   ├── models.py        # Data models
│   └── coordination.py  # Cross-generator consistency
├── logging/             # Structured JSON logging
├── util/                # Seed management
└── config/              # YAML configuration presets

data/
├── raw/                 # Generator outputs (JSON Lines)
├── manifests/           # Batch metadata, seeds, dataset descriptors
└── staged/              # (Future) Spark processed data

docker/
├── docker-compose.yml   # Multi-container orchestration
└── Dockerfile.generator # Python runtime image

specs/001-driving-batch-generators/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan
├── data-model.md        # Entity definitions
└── quickstart.md        # Detailed setup guide
```

## Reproducibility

To reproduce a dataset exactly:
1. Use the same `--seed` value
2. Apply identical configuration parameters
3. Run generators in order (companies → driver events)

Seeds are automatically recorded in `data/manifests/dataset.md` and `batch_meta.json`.

## Randomness Model

- **Event counts**: Poisson distribution (λ = `event_rate_per_driver`)
- **Event types**: Weighted categorical (start driving: 40%, stopped: 35%, delivered: 25%)
- **Timestamps**: Uniform within 15-minute interval boundaries
- **Company onboarding**: Independent hourly cadence (configurable)

## Testing

```powershell
# Install dependencies locally
pip install -r requirements.txt

# Run unit tests
pytest tests/unit/

# Run with coverage
pytest --cov=src tests/

# Type checking (strict mode)
mypy src/
```

**Type Safety**: All Python code uses comprehensive type annotations. Type checking enforced via `mypy --strict` with zero errors tolerated.

## Documentation

- [Full Specification](specs/001-driving-batch-generators/spec.md)
- [Implementation Plan](specs/001-driving-batch-generators/plan.md)
- [Detailed Quickstart](specs/001-driving-batch-generators/quickstart.md)
- [Data Model](specs/001-driving-batch-generators/data-model.md)

## Roadmap

**Current (v0.1)**: JSON Lines generation, local Docker environment

**Next**:
- Spark ingestion of JSON Lines → Delta tables
- Multi-geo support (EU, SA, AUS)
- Company deactivation lifecycle
- Performance benchmarking framework

## License

MIT (for experimentation and learning)

## Troubleshooting HTTP & Data

| Symptom | Cause | Fix |
|---------|-------|-----|
| `curl : (7) Failed to connect` | Container not started | `docker compose ps`; `docker compose up -d` |
| `/api/clean` returns 400 | Not paused | `curl -X POST /api/pause` then retry |
| Logs empty | No batches yet / path cleared | Wait for next interval or inspect `data/manifests/logs` |
| `idle_seconds` is null | No previous batch timestamp | Allow first batch to complete |
| Since filter returns all logs | Timestamp not URL-encoded | Use `[uri]::EscapeDataString($since)` |

## HTTP Response Schema (Health)

Subset of `GET /api/health` response (validated with Pydantic):

```jsonc
{
  "status": "running|paused",
  "timestamp": "ISO8601",
  "uptime": { "seconds": 12.34, "hours": 0.01, "start_time": "ISO8601" },
  "company_generator": { "total_batches": 1, "last_batch_time": "ISO8601", "idle_seconds": 5.7 },
  "driver_generator": { "total_batches": 3, "last_batch_time": "ISO8601", "last_interval_end": "ISO8601", "idle_seconds": 2.1 },
  "lifecycle": { "paused": false, "shutdown_requested": false },
  "state": { "last_saved": "ISO8601", "state_file": "data/manifests/generator_state.json" }
}
```

  ### Auto Reinitialization Metadata

  If `/clean` removed baseline files (`companies.jsonl`, driver events directory) the **first** subsequent `/resume` performs immediate one-time regeneration:

  1. Writes new `companies.jsonl` with configured `number_of_companies`
  2. Generates an initial driver event batch for current 15‑minute interval

  Metadata appears in both `/api/resume` response and later `/api/health` calls:

  ```jsonc
  "auto_reinit": {
    "performed": true,
    "at": "2025-11-08T12:34:56.789Z",
    "actions": ["companies:100", "driver_batch:1"],
    "missing_files": ["data/raw/companies.jsonl", "data/raw/events"]
  }
  ```

  Fields:
  - `performed`: Whether auto reinit occurred (sticky after first time)
  - `at`: Timestamp regeneration completed
  - `actions`: Summary of regenerated artifacts or error markers
  - `missing_files`: Which paths triggered regeneration

  Idempotence: Subsequent `/resume` calls do not regenerate again unless container restarts and baseline is missing anew.
