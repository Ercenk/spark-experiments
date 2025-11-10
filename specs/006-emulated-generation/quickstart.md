# Quickstart: Emulated Fast-Cadence Data Generation

**Feature**: 006-emulated-generation  
**Audience**: Data pipeline developers  
**Time to complete**: 5 minutes  
**Prerequisites**: Docker, Docker Compose, running generator container

## What is Emulated Mode?

Emulated mode generates **small batches** (5-20 records) at **rapid intervals** (5-10 seconds) instead of production-scale batches (100+ records) at longer intervals (15 minutes, hourly). This enables you to observe the complete medallion pipeline (bronze → silver → gold) in near real-time for faster development feedback.

**Use Cases**:
- Testing pipeline transformations without waiting 15+ minutes between batches
- Debugging quality injection logic with visible results in seconds
- Demonstrating pipeline flow to stakeholders
- Validating dashboard real-time updates

---

## Quick Start (3 Steps)

### Step 1: Enable Emulated Mode

Create or use the provided emulated configuration:

```bash
# Use existing emulated config
cp src/config/config.emulated.yaml src/config/config.active.yaml

# Or create your own
cat > src/config/config.active.yaml <<EOF
seed: 42
number_of_companies: 100        # Production value (unused when emulated)
drivers_per_company: 10
event_rate_per_driver: 3.5
company_onboarding_interval: PT1H   # Production value
driver_event_interval: PT15M        # Production value

# Enable emulated mode
emulated_mode:
  enabled: true
  company_batch_interval: PT10S   # 10-second cadence
  driver_batch_interval: PT10S
  companies_per_batch: 10
  events_per_batch_min: 5
  events_per_batch_max: 20

# Optional: Enable quality injection
quality_injection:
  enabled: true
  corruption_rate: 0.3
EOF
```

### Step 2: Start Generator

```powershell
cd docker
docker compose up generator

# Or in detached mode
docker compose up -d generator
```

**Expected Output** (within 10 seconds):

```
generator_1 | 2025-11-09T12:00:10.123Z INFO Starting generator in emulated mode
generator_1 | 2025-11-09T12:00:10.456Z INFO Company batch 1: 10 companies generated
generator_1 | 2025-11-09T12:00:10.789Z INFO Driver batch 1: 15 events generated
generator_1 | 2025-11-09T12:00:20.234Z INFO Company batch 2: 10 companies generated
generator_1 | 2025-11-09T12:00:20.567Z INFO Driver batch 2: 12 events generated
```

### Step 3: Observe Batches

```powershell
# Watch batch directories appear in real-time
docker compose exec generator sh -c "watch -n 1 'ls -lt /data/raw/events | head -10'"

# Check health status (includes emulated mode indicator)
curl.exe -s http://localhost:18000/api/health | jq '{mode:.generation_mode, batches:.company_generator.total_batches}'

# Expected output:
# {
#   "mode": "emulated",
#   "batches": 12
# }

# View recent logs
curl.exe -s "http://localhost:18000/api/logs?limit=5" | jq '.entries[] | {time:.timestamp, msg:.message}'
```

---

## Detailed Configuration Options

### Emulated Mode Fields

| Field | Default | Range | Description |
|-------|---------|-------|-------------|
| `enabled` | `false` | `true`/`false` | Toggle emulated mode |
| `company_batch_interval` | `"PT10S"` | `"PT1S"` to `"PT1H"` | Company onboarding interval (ISO 8601) |
| `driver_batch_interval` | `"PT10S"` | `"PT1S"` to `"PT1H"` | Driver event interval (ISO 8601) |
| `companies_per_batch` | `10` | 1 to 100 | Companies generated per batch |
| `events_per_batch_min` | `5` | 1+ | Minimum driver events per batch |
| `events_per_batch_max` | `20` | ≥ min | Maximum driver events per batch |

### Example Configurations

**Ultra-Fast (5-second cadence)**:

```yaml
emulated_mode:
  enabled: true
  company_batch_interval: PT5S
  driver_batch_interval: PT5S
  companies_per_batch: 5
  events_per_batch_min: 3
  events_per_batch_max: 10
```

**Moderate (30-second cadence)**:

```yaml
emulated_mode:
  enabled: true
  company_batch_interval: PT30S
  driver_batch_interval: PT30S
  companies_per_batch: 20
  events_per_batch_min: 10
  events_per_batch_max: 50
```

---

## Observing the Pipeline

### 1. Real-Time Batch Monitoring

```powershell
# Count batches generated in last minute
docker compose exec generator sh -c "
  find /data/raw/events -name 'batch_meta.json' -mmin -1 | wc -l
"

# Expected: ~6 batches (10-second intervals)
```

### 2. Dashboard Metrics (if available)

Open dashboard at http://localhost:3000 (if frontend deployed):

- **Batch Counter**: Increments every 10 seconds
- **Quality Metrics**: Shows real-time corruption percentages
- **Processing Latency**: Bronze → Silver → Gold timings

### 3. Log Analysis

```powershell
# Extract batch sizes from logs
docker compose logs generator | grep "batch.*generated" | tail -10

# Example output:
# Company batch 1: 10 companies generated
# Driver batch 1: 15 events generated (8 valid, 7 corrupted)
# Company batch 2: 10 companies generated
# Driver batch 2: 12 events generated (7 valid, 5 corrupted)
```

---

## Switching Between Modes

### Production → Emulated

```powershell
# 1. Stop generator
docker compose stop generator

# 2. Update config
cp src/config/config.emulated.yaml src/config/config.active.yaml

# 3. Restart generator
docker compose up -d generator

# 4. Verify mode
curl.exe http://localhost:18000/api/health | jq .generation_mode
# Output: "emulated"
```

### Emulated → Production

```powershell
# 1. Stop generator
docker compose stop generator

# 2. Update config
cp src/config/config.base.yaml src/config/config.active.yaml

# 3. Restart generator
docker compose up -d generator

# 4. Verify mode
curl.exe http://localhost:18000/api/health | jq .generation_mode
# Output: "production"
```

---

## Troubleshooting

### Problem: Batches not generating

**Symptoms**: No new directories in `/data/raw/events/`

**Checks**:

```powershell
# 1. Verify emulated mode enabled
docker compose exec generator sh -c "cat /app/src/config/config.active.yaml | grep 'enabled: true'"

# 2. Check generator status
curl.exe http://localhost:18000/api/health | jq '{status, mode:.generation_mode}'

# 3. View recent errors
curl.exe "http://localhost:18000/api/logs?level=error&limit=10" | jq '.entries'
```

**Solution**: Ensure `emulated_mode.enabled: true` in config, restart container.

---

### Problem: Batches too fast/slow

**Symptoms**: Intervals don't match configuration

**Diagnosis**:

```powershell
# Check configured interval
docker compose exec generator sh -c "cat /app/src/config/config.active.yaml | grep batch_interval"

# Measure actual interval from logs
docker compose logs generator --tail 20 | grep "batch.*generated"
```

**Solution**: Verify ISO 8601 format (e.g., `PT10S` not `10S`), adjust interval value.

---

### Problem: Validation errors on startup

**Symptoms**: Generator exits with config error

**Example Error**:

```
ERROR Config validation failed: Emulated interval must be >= 1 second, got 0:00:00.500000
```

**Solution**: Fix interval in config file (minimum 1 second):

```yaml
# WRONG
company_batch_interval: PT0.5S  # Not supported

# CORRECT
company_batch_interval: PT1S    # Minimum 1 second
```

---

## Performance Expectations

### Resource Usage (1-hour emulated run)

| Metric | Production (1 hour) | Emulated (1 hour) | Notes |
|--------|---------------------|-------------------|-------|
| Batches generated | 5 (1 company + 4 driver) | 720 (360 company + 360 driver) | 144x increase |
| Disk space | ~50 MB | ~200 MB | Mostly batch metadata |
| Memory usage | ~30 MB | ~35 MB | Minimal increase (batches flushed to disk) |
| CPU usage | <5% | <10% | More frequent I/O |

### Timing Precision

| Interval | Expected Variance | Measured (Linux) | Measured (Windows) |
|----------|-------------------|------------------|-------------------|
| 10 seconds | <1% | ±15-50ms | ±15-100ms |
| 5 seconds | <2% | ±12-45ms | ±15-90ms |

---

## Validation Commands

### Test 1: Verify Emulated Intervals

```powershell
# Generate for 1 minute, count batches
docker compose up -d generator
Start-Sleep -Seconds 60
docker compose exec generator sh -c "ls /data/raw/events | wc -l"

# Expected: ~12 batches (6 company + 6 driver at 10s intervals)
```

### Test 2: Verify Batch Sizes

```powershell
# Check recent company batch size
docker compose exec generator sh -c "
  latest=\$(ls -t /data/raw/events | head -1)
  cat /data/raw/events/\$latest/batch_meta.json | jq .record_count
"

# Expected: 5-20 (within configured range)
```

### Test 3: Verify Schema Compatibility

```powershell
# Generate emulated batch
docker compose exec generator python -m pytest tests/integration/test_emulated_mode.py::test_schema_compatibility

# Expected: PASSED (schemas identical to production)
```

---

## Next Steps

After verifying emulated mode works:

1. **Implement Pipeline**: Use emulated batches to test bronze → silver transformations
2. **Quality Validation**: Verify pipeline correctly handles corrupted records
3. **Dashboard Integration**: Connect dashboard to observe real-time metrics
4. **Performance Testing**: Run 1-hour emulated session to validate sustained operation

---

## Reference Commands

### Start/Stop

```powershell
# Start emulated generation
docker compose up -d generator

# View logs
docker compose logs -f generator

# Stop generation
docker compose stop generator

# Clean data (requires generator stopped)
docker compose exec generator sh -c "rm -rf /data/raw/events/* /data/raw/companies.jsonl"
```

### Monitoring

```powershell
# Health check
curl.exe http://localhost:18000/api/health | jq

# Batch count
curl.exe http://localhost:18000/api/health | jq '{company:.company_generator.total_batches, driver:.driver_generator.total_batches}'

# Recent logs
curl.exe "http://localhost:18000/api/logs?limit=10" | jq '.entries[] | {time:.timestamp, msg:.message}'
```

### Configuration

```powershell
# View active config
docker compose exec generator sh -c "cat /app/src/config/config.active.yaml"

# Validate config
docker compose exec generator python -c "
from src.generators.config import Config
config = Config.from_yaml('src/config/config.active.yaml')
print(f'Mode: {\"emulated\" if config.emulated_mode.enabled else \"production\"}')
print(f'Company interval: {config.active_company_interval}')
print(f'Driver interval: {config.active_driver_interval}')
"
```

---

## FAQ

**Q: Can I mix production and emulated batches in the same dataset?**  
A: Not recommended. Generated data depends on previous state (e.g., eligible companies for driver events). Switch modes only when starting fresh or after cleaning data.

**Q: Does emulated mode affect seed reproducibility?**  
A: No. Seeds are calculated identically (`base_seed + batch_counter`). Same seed in same mode reproduces same data.

**Q: Can I use emulated mode for production?**  
A: No. Emulated mode is for development/testing only. Production requires realistic intervals and batch sizes for representative metrics.

**Q: How do I clean emulated batches without affecting production data?**  
A: Use `/api/clean` endpoint (requires pause first) or manually delete specific batch directories.

---

## Additional Resources

- [Feature Specification](spec.md): Complete requirements and user stories
- [Implementation Plan](plan.md): Technical architecture and phases
- [Data Model](data-model.md): Configuration schema and entities
- [API Contracts](contracts/api-enhancements.md): Enhanced endpoint documentation
