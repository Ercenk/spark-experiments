# Medallion Pipeline Structure (Placeholder)

This document outlines the planned directories.
No implementation code yet.

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

Data tables will live under:
```
data/processed/medallion/bronze/
data/processed/medallion/silver/
data/processed/medallion/gold/
```
