# Data Model: Emulated Fast-Cadence Data Generation

**Feature**: 006-emulated-generation  
**Created**: 2025-11-09  
**Status**: Design

## Overview

This feature introduces **no new data entities**—it operates on the same data structures as production mode with different **configuration parameters** and **generation frequencies**. All schemas, validation rules, and serialization formats remain identical.

## Configuration Entities

### EmulatedModeConfig

**Purpose**: Group all emulation-specific parameters to enable fast-cadence generation for development/testing.

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `enabled` | `bool` | Required | Whether emulated mode is active (default: `false`) |
| `company_batch_interval` | `str` | ISO 8601 duration, ≥1s | Company onboarding interval (default: `"PT10S"`) |
| `driver_batch_interval` | `str` | ISO 8601 duration, ≥1s | Driver event batch interval (default: `"PT10S"`) |
| `companies_per_batch` | `int` | 1 ≤ value ≤ 100 | Number of companies per batch (default: `10`) |
| `events_per_batch_min` | `int` | ≥1 | Minimum driver events per batch (default: `5`) |
| `events_per_batch_max` | `int` | ≥1, ≥ min | Maximum driver events per batch (default: `20`) |

**Relationships**:
- Nested within parent `Config` model via `emulated_mode` field
- Overrides production-mode interval/size fields when `enabled=true`

**Validation Rules**:
- `company_batch_interval` and `driver_batch_interval` must parse to `timedelta` ≥1 second
- `events_per_batch_max` must be ≥ `events_per_batch_min`
- All intervals must match ISO 8601 pattern: `^PT(\d+H)?(\d+M)?(\d+S)?$`

**State Transitions**: None (configuration is immutable at runtime; changes require restart)

### Config (Enhanced)

**Changes to Existing Entity**:

| New/Modified Field | Type | Description |
|-------------------|------|-------------|
| `driver_event_interval` | `str` | Production driver event interval (new field, default: `"PT15M"`) |
| `emulated_mode` | `EmulatedModeConfig` | Nested emulation config (new field, default: disabled) |

**Computed Properties** (read-only):

| Property | Return Type | Logic |
|----------|-------------|-------|
| `active_company_interval` | `str` | `emulated_mode.company_batch_interval` if enabled, else `company_onboarding_interval` |
| `active_driver_interval` | `str` | `emulated_mode.driver_batch_interval` if enabled, else `driver_event_interval` |
| `active_company_count` | `int` | `emulated_mode.companies_per_batch` if enabled, else `number_of_companies` |

**Backward Compatibility**: Existing configs without `emulated_mode` field use default (disabled), preserving production behavior.

## Data Schemas (Unchanged)

The following entities **remain identical** between production and emulated modes:

### Company

| Field | Type | Notes |
|-------|------|-------|
| `company_id` | `str` | UUID format |
| `company_name` | `str` | Synthetic name |
| `onboarding_date` | `datetime` | ISO 8601 timestamp |
| `region` | `str` | Enum: NA, EU, AUS, SA |
| `drivers_count` | `int` | Number of drivers |

**Emulated Mode Differences**: Only batch frequency and quantity change; schema identical.

### DriverEventRecord

| Field | Type | Notes |
|-------|------|-------|
| `driver_id` | `str` | UUID format |
| `company_id` | `str` | Foreign key to Company |
| `event_type` | `str` | Enum: start_driving, stopped_driving, delivered |
| `event_timestamp` | `datetime` | ISO 8601 timestamp |
| `location` | `dict` | lat, lon coordinates (nullable) |

**Emulated Mode Differences**: Only event rate and batch size change; schema identical.

### BatchMetadata

| Field | Type | Notes |
|-------|------|-------|
| `batch_id` | `str` | Format: `YYYYMMDDTHHMMSSZ` |
| `interval_start` | `datetime` | Batch interval start time |
| `interval_end` | `datetime` | Batch interval end time |
| `record_count` | `int` | Total events in batch (valid + corrupted) |
| `valid_count` | `int` | Valid events count |
| `corrupted_count` | `int` | Corrupted events count |
| `seed` | `int` | RNG seed for reproducibility |
| `generation_timestamp` | `datetime` | When batch was generated |

**Emulated Mode Differences**: 
- `interval_start` and `interval_end` span shorter periods (5-10 seconds vs. 15 minutes)
- `record_count` smaller (5-20 vs. 100s-1000s)
- Batch ID granularity: second-level precision required (existing `%Y%m%dT%H%M%SZ` format includes seconds)

## Metadata Extensions (Optional)

To improve observability, batch metadata MAY include mode indicator:

| New Field | Type | Description |
|-----------|------|-------------|
| `generation_mode` | `str` | Enum: `"production"`, `"emulated"` (optional) |

**Rationale**: Enables post-processing to filter emulated batches from production analytics.

## Filesystem Layout (Unchanged)

```
data/
├── raw/
│   ├── companies.jsonl              # Company records (one per line)
│   └── events/
│       ├── 20241109T120000Z/        # Production batch (15-min interval)
│       │   ├── events.jsonl
│       │   └── batch_meta.json
│       ├── 20241109T120010Z/        # Emulated batch (+10 seconds)
│       │   ├── events.jsonl
│       │   └── batch_meta.json
│       └── 20241109T120020Z/        # Emulated batch (+10 seconds)
│           ├── events.jsonl
│           └── batch_meta.json
└── manifests/
    ├── generator_state.json         # Last batch counters/timestamps
    ├── batch_manifest.json          # Cumulative counts
    └── logs/
        └── 2024-11-09/
            └── generator.jsonl      # Daily log rotation
```

**Emulated Mode Impact**:
- Higher directory count in `events/` (360/hour vs. 4/hour)
- Batch IDs differ by seconds instead of minutes
- No schema changes to file contents

## Quality Injection Compatibility

**Entities Affected**: `Company`, `DriverEventRecord` (via quality injection framework)

**Emulated Mode Behavior**:
- Same quality injection rules apply (missing fields, nulls, malformed timestamps, invalid enums)
- Corruption rate configurable via `quality_injection` config section (existing)
- Smaller batches mean fewer total corrupted records, same percentage

**Example**:
- Production: 100 companies, 60% corruption rate → 60 corrupted records
- Emulated: 10 companies, 60% corruption rate → 6 corrupted records

**Schema**: Corrupted records are raw `dict` objects (not typed), same as production.

## Assumptions

1. **No New Entities**: Emulated mode is purely a timing/sizing variation, not a new data domain
2. **Backward Compatibility**: Existing pipeline code (bronze → silver → gold) processes emulated batches identically to production batches
3. **Seed Independence**: Each batch uses independent seed (`base_seed + batch_counter`), mode does not affect seed calculation
4. **Filesystem Capacity**: System can handle 700+ subdirectories per hour (validated for ext4, NTFS)

## Validation Queries

To verify data consistency between modes:

```python
# Check schema compatibility
production_batch = load_batch("20241109T120000Z")  # 15-min production batch
emulated_batch = load_batch("20241109T120010Z")    # 10-sec emulated batch

assert production_batch[0].keys() == emulated_batch[0].keys()  # Same fields
assert type(production_batch[0]['event_timestamp']) == type(emulated_batch[0]['event_timestamp'])  # Same types

# Check quality injection consistency
production_corrupted = [r for r in production_batch if not validate(r)]
emulated_corrupted = [r for r in emulated_batch if not validate(r)]

assert set(production_corrupted[0].keys()) == set(emulated_corrupted[0].keys())  # Same corruption patterns
```

## References

- [Existing Config Model](../../src/generators/config.py): Base `Config` class structure
- [Quality Injection Config](../../src/generators/quality_injection.py): Nested config pattern example
- [Batch Metadata Format](../../src/generators/models.py): `BatchMetadata` class definition
