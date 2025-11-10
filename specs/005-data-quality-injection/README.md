# Data Quality Injection (Feature 005)

## Overview

Adds configurable data quality issue injection to the generator system for testing data pipeline validation and cleansing capabilities.

## Purpose

Real-world data often contains quality issues. This feature allows you to:

- **Test pipeline robustness**: Verify your Spark jobs handle malformed data correctly
- **Validate cleansing logic**: Ensure deduplication, null handling, and validation work as expected
- **Reproduce issues deterministically**: Using the same seed guarantees repeatable error injection
- **Measure data quality metrics**: Track what types of issues occur and at what rates

## Configuration

Add a `quality_injection` section to your config YAML:

```yaml
quality_injection:
  enabled: true
  error_rate: 0.15  # 15% of records will have issues
  
  # Specific issue probabilities (when error_rate triggers)
  missing_field_probability: 0.3
  null_value_probability: 0.3
  malformed_timestamp_probability: 0.2
  invalid_enum_probability: 0.1
  duplicate_probability: 0.05
  boundary_violation_probability: 0.05
  
  # Scope control
  inject_in_driver_events: true
  inject_in_companies: true
  
  # Logging
  log_injected_issues: true
```

### Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `enabled` | `false` | Master switch for quality injection |
| `error_rate` | `0.0` | Probability (0.0-1.0) that a record has at least one issue |
| `missing_field_probability` | `0.3` | Remove a required field entirely |
| `null_value_probability` | `0.3` | Replace field value with `null` |
| `malformed_timestamp_probability` | `0.2` | Corrupt timestamp format (invalid month/day, missing timezone, etc.) |
| `invalid_enum_probability` | `0.1` | Use invalid enumeration value (e.g., "UNKNOWN_EVENT" for event_type) |
| `duplicate_probability` | `0.05` | Create intentional duplicate records |
| `boundary_violation_probability` | `0.05` | Generate timestamp outside valid interval bounds |
| `inject_in_driver_events` | `true` | Apply injection to driver event records |
| `inject_in_companies` | `true` | Apply injection to company records |
| `log_injected_issues` | `true` | Log each injected issue with details |

## Issue Types

### Missing Fields
Removes a field entirely from the record. Tests pipeline handling of incomplete data.

**Example**:
```json
// Original
{"driver_id": "DRV-001", "event_type": "start driving", "timestamp": "2024-01-01T12:00:00Z"}

// After injection
{"event_type": "start driving", "timestamp": "2024-01-01T12:00:00Z"}
```

### Null Values
Replaces a field value with `null`. Tests null-handling logic in transformations.

**Example**:
```json
{"driver_id": "DRV-001", "event_type": null, "timestamp": "2024-01-01T12:00:00Z"}
```

### Malformed Timestamps
Corrupts timestamp format with various realistic errors:
- Invalid month/day (e.g., `2024-13-01`, `2024-01-32`)
- Invalid hour (e.g., `2024-01-01T25:00:00Z`)
- Missing timezone
- Wrong date separators
- Complete garbage values

**Example**:
```json
{"driver_id": "DRV-001", "event_type": "start driving", "timestamp": "2024-13-01T00:00:00Z"}
```

### Invalid Enums
Replaces enumeration values with invalid alternatives.

**Example**:
```json
{"driver_id": "DRV-001", "event_type": "UNKNOWN_EVENT", "timestamp": "2024-01-01T12:00:00Z"}
```

## Usage

### Basic Usage

1. Create or modify a config file with quality injection enabled:

```bash
cp src/config/config.base.yaml src/config/config.quality_test.yaml
# Edit config.quality_test.yaml to add quality_injection section
```

2. Run generators with the modified config:

```bash
# Generate companies with quality issues
python -m src.generators.company_generator \
  --config src/config/config.quality_test.yaml \
  --output data/raw/companies.jsonl \
  --seed 42

# Generate driver events with quality issues
python -m src.generators.driver_event_generator \
  --config src/config/config.quality_test.yaml \
  --output data/raw/events \
  --companies data/raw/companies.jsonl \
  --seed 42 \
  --now
```

3. Run the medallion pipeline to see cleansing in action:

```bash
python -m src.pipeline.medallion.bronze_to_silver \
  --bronze-path data/raw \
  --silver-path data/silver \
  --verbose
```

### Recommended Testing Workflow

#### Phase 1: No Quality Issues (Baseline)
```yaml
quality_injection:
  enabled: false
```

Run pipeline to establish baseline metrics.

#### Phase 2: Low Error Rate (5%)
```yaml
quality_injection:
  enabled: true
  error_rate: 0.05
```

Verify pipeline handles occasional errors gracefully.

#### Phase 3: Medium Error Rate (15%)
```yaml
quality_injection:
  enabled: true
  error_rate: 0.15
```

Test realistic production scenarios with moderate data quality issues.

#### Phase 4: High Error Rate (50%)
```yaml
quality_injection:
  enabled: true
  error_rate: 0.50
```

Stress test pipeline with extreme quality problems.

## Logging and Observability

When `log_injected_issues: true`, each injected issue is logged:

```json
{
  "level": "WARNING",
  "message": "Quality issue injected: null_value in driver_event_DRV-001_2024-01-01T12:00:00Z.event_type (NULL_INJECTION): start driving → null",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

After each batch, a summary is logged:

```json
{
  "level": "INFO",
  "message": "Quality injection summary",
  "metadata": {
    "interval_start": "2024-01-01T12:00:00Z",
    "total_events": 100,
    "issues_injected": 15,
    "issue_breakdown": {
      "null_value": 5,
      "missing_field": 4,
      "malformed_timestamp": 3,
      "invalid_enum": 2,
      "boundary_violation": 1
    }
  }
}
```

## Reproducibility

Quality injection uses the **same RandomState** as the generator, ensuring:

- **Same seed → same errors**: Running with `--seed 42` always injects the same issues
- **Deterministic testing**: Test cases are reproducible
- **Debugging**: You can re-run failed batches with identical errors

## Integration with Medallion Pipeline

The medallion pipeline's validation logic (in `src/pipeline/medallion/bronze_to_silver/transformations/validation.py`) detects and flags these issues:

```python
# Each record gets quality flags
is_valid_timestamp = check_timestamp_format(record.timestamp)
is_valid_enum = record.event_type in VALID_EVENT_TYPES
is_complete = all(required_fields_present)

# Add quality columns to Silver
record['quality_is_valid'] = is_valid_timestamp and is_valid_enum and is_complete
record['quality_flags'] = build_flags_array(...)
```

You can then query Silver to analyze data quality:

```sql
SELECT 
  quality_is_valid,
  quality_flags,
  COUNT(*) as record_count
FROM silver.driver_events
GROUP BY quality_is_valid, quality_flags
ORDER BY record_count DESC
```

## Architecture

```
┌─────────────────────────┐
│ Generator Configuration │
│  (config.yaml)          │
└───────────┬─────────────┘
            │
            │ includes quality_injection settings
            ▼
┌─────────────────────────┐
│ Generator               │
│ (company_generator,     │
│  driver_event_generator)│
└───────────┬─────────────┘
            │
            │ creates
            ▼
┌─────────────────────────┐
│ QualityInjector         │
│ (uses same RNG as       │
│  generator for repro)   │
└───────────┬─────────────┘
            │
            │ post-processes records
            ▼
┌─────────────────────────┐
│ Output (JSONL)          │
│ - Some valid records    │
│ - Some with issues      │
└─────────────────────────┘
            │
            │ consumed by
            ▼
┌─────────────────────────┐
│ Medallion Pipeline      │
│ - Validation flags      │
│ - Cleansing logic       │
│ - Quality metrics       │
└─────────────────────────┘
```

## Files

- `src/generators/quality_injection.py` - Configuration models
- `src/generators/injector.py` - Injection logic
- `src/generators/config.py` - Extended to include `quality_injection` field
- `src/generators/driver_event_generator.py` - Integrated quality injection
- `src/generators/company_generator.py` - Integrated quality injection
- `src/config/config.quality_injection.yaml` - Example configuration
- `tests/unit/test_quality_injection.py` - Unit tests

## Testing

Run unit tests:

```bash
python -m pytest tests/unit/test_quality_injection.py -v
```

## Future Enhancements

Potential additions in future iterations:

- **Duplicate injection**: Actually create duplicate records (currently designed but not fully implemented)
- **Schema drift**: Add extra fields not in the schema
- **Encoding issues**: Inject UTF-8/ASCII encoding problems
- **Numeric boundary violations**: Out-of-range values for numeric fields
- **Referential integrity**: Create driver events for non-existent companies
- **Write malformed JSON directly**: Currently invalid records are skipped; could write raw JSON to test parser robustness

## Related Specifications

- `specs/005-data-quality-injection/spec.md` - Full specification
- `specs/004-medallion-pipeline/spec.md` - Validation and cleansing in Spark pipeline
- `specs/001-driving-batch-generators/spec.md` - Base generator system
