# Quickstart: Driving Batch Generators

This guide explains how to run the Python data generators locally to produce JSON Lines batches. Initial iteration focuses on raw data generation; Spark processing and Delta ingestion are deferred to future phases.

## Prerequisites
- Docker & Docker Compose installed
- Git clone of repository
- Adequate local disk space (~500MB for initial experiments)

## Directory Layout (Emulated ADLS Hierarchy)
```
/data/
  raw/          # JSON Lines generator outputs (companies.jsonl, events/<batch_id>/events.jsonl)
  staged/       # (Deferred) Spark curated tables
  processed/    # (Deferred) Aggregated analytics
  manifests/    # Batch manifests, dataset metadata, seed files
```

## Step 1: Configure Simulation
Create/edit `src/generators/config.yaml` (example):
```yaml
seed: 42
number_of_companies: 100
drivers_per_company: 10
event_rate_per_driver: 3.5  # avg events per 15-min interval
company_onboarding_interval: PT1H
```

## Step 2: Launch Environment
```bash
docker compose up -d
```
Services expected:
- spark-driver
- spark-executor-1
- generator (python) - runs continuously and auto-generates initial companies

The generator container automatically generates the initial company batch on first startup if `companies.jsonl` doesn't exist or is empty.

## Step 3: Monitor Generator Status
Check the health and status of the running generators:
```bash
curl http://localhost:18000/status | python -m json.tool
```

This returns comprehensive statistics including:
- Generator status (running/paused)
- Uptime in seconds and hours
- Company generator: total batches, last batch time, idle seconds
- Driver generator: total batches, last batch time, idle seconds
- Lifecycle state and state file location

## Step 4: Runtime Control via REST API

The generator runs continuously, but you can control it via REST API:

### Pause Generation
```bash
curl -X POST http://localhost:18000/pause
```
Response: `{"success": true, "message": "Generator paused successfully", "status": "paused"}`

### Resume Generation
```bash
curl -X POST http://localhost:18000/resume
```
Response: `{"success": true, "message": "Generator resumed successfully", "status": "running"}`

### Clean All Data (requires paused state)
```bash
# First pause the generator
curl -X POST http://localhost:18000/pause

# Then clean the data
curl -X POST http://localhost:18000/clean
```
Response includes deleted items, counts, and cleanup status. After cleaning, restart the container:
```bash
docker compose restart generator
```

## Step 5: Spark Ingestion (Deferred)
*This step is deferred to a future iteration. Initial scope produces raw JSON Lines only.*

Once implemented, Spark processing will transform JSON Lines batches into Delta tables:
```bash
# (Future command - not yet operational)
docker compose exec spark-driver spark-submit /app/src/spark_jobs/batch_ingest.py --source /data/raw/events --target /data/staged/events_delta
```
Writes curated Delta table to staged zone.

## Reproducibility
- Provide identical `--seed` to reproduce onboarding and first interval batch.
- Manifest file `manifests/batch_manifest.json` tracks last batch and cumulative stats.

## Step 5: View Generated Data
Check the generated companies and event batches:
```bash
# View companies
docker compose exec generator sh -c "head -n 5 /data/raw/companies.jsonl"

# List event batches
docker compose exec generator sh -c "ls -lh /data/raw/events/"

# View a specific batch
docker compose exec generator sh -c "cat /data/raw/events/<batch_id>/batch_meta.json"
```

## Logs & Metrics
- JSON Lines logs written to both stdout (visible via `docker logs`) and `manifests/logs/<date>/generator.log.jsonl`.
- Each entry: `{timestamp, component, run_id, level, message, metadata}`.
- Real-time monitoring via container logs:
  ```bash
  docker compose logs -f generator
  ```

## REST API Endpoints

The generator exposes the following REST API endpoints on port 18000:

| Endpoint | Method | Purpose | Response |
|----------|--------|---------|----------|
| `/health` | GET | Health check with detailed stats | JSON with status, uptime, batch counts |
| `/status` | GET | Alias for /health | Same as /health |
| `/pause` | POST | Pause generation | JSON with success status |
| `/resume` | POST | Resume generation | JSON with success status |
| `/clean` | POST | Clean all data (requires paused) | JSON with deleted items |

## Teardown
```bash
# Stop and remove containers (keep data)
docker compose down

# Stop and remove containers AND data volumes
docker compose down -v
```

Alternatively, use the REST API to clean data while keeping containers running:
```bash
curl -X POST http://localhost:18000/pause
curl -X POST http://localhost:18000/clean
docker compose restart generator
```

## Next Steps
- Adjust configuration to scale drivers_per_company.
- Use pause/resume endpoints to control generation without restarting containers.
- Monitor health endpoint for batch statistics and idle time tracking.
- Introduce multi-geo and company deactivation in future iteration.
- Add performance measurements (event generation time vs batch size).
