# Implementation Plan: Medallion Data Pipeline

**Feature**: Medallion Data Pipeline
**Branch**: 004-medallion-pipeline
**Date**: 2025-11-09

## Technical Stack
- Python 3.11
- Apache Spark 3.5 (local cluster / driver mode for MVP)
- delta-spark for Delta Lake table management
- Logging: Python standard logging with JSON formatter (future enhancement)
- Validation: Simple Spark DataFrame filters (future option: Great Expectations)

## Directory Structure
```
pipeline/medallion/
  bronze_ingest/
  bronze_to_silver/
    jobs/
    transformations/
    schemas/
  silver_experiments/
    variant_a/
      transformations/
    variant_b/
      transformations/
    common/
    metrics/
  silver_to_gold/
    jobs/
    aggregations/
    schemas/
  gold_outputs/
  testing/
    fixtures/
    expected/
  docs/
```
Data output paths:
```
data/processed/medallion/bronze/
data/processed/medallion/silver/
data/processed/medallion/gold/
```

## Phases Overview
- Phase 1 Setup: Create package inits, constants, utilities.
- Phase 2 Foundational: Schema placeholders, manifest & lineage utilities.
- Phase 3 (US1): Raw JSON → Silver curated driver events & companies.
- Phase 4 (US2): Silver join enrichment producing Gold enriched driver events.
- Phase 5 (US3): Lineage and audit expansion.
- Phase 6 Polish: docs, performance wrappers, deployment scripts.

## Key Decisions
- Ingestion runs batch (not streaming) for MVP.
- Deduplication key: (driver_id, event_timestamp).
- Company enrichment: left join; unmatched flagged.
- Lineage captured via manifest + per-record source file columns.

## Open Future Enhancements
- Swap batch dedup logic with incremental state store.
- Add data quality expectations framework.
- Introduce streaming ingestion (Structured Streaming) if needed.
- Partition strategy tuning based on volume.

## Risks & Mitigations
- Volume uncertainty → start with non-partitioned tables; revisit.
- Schema evolution → restrict to additive columns; enforce consistent schemas.

## MVP Definition
Deliver Phase 3 (User Story 1) with runnable ingestion producing Silver tables and manifest artifacts.

