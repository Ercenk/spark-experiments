# Experiment 001: Baseline Batch Generation Performance

**Date**: 2025-11-08
**Feature**: Driving Batch Generators (v0.1)

## Hypothesis

Baseline batch generation completes in <5 seconds for ~5,000 events (100 companies × 10 drivers × 3.5 avg events).

## Metrics to Collect

| Metric | Expected | Measurement Method |
|--------|----------|-------------------|
| Generation time | <5s | Wall clock (batch_meta.generation_time - interval_start) |
| Event count | ~5000 ± 10% | Actual count in events.jsonl |
| Memory usage | <512MB | Docker stats during generation |
| Batch file size | ~1-2MB | du -h on batch directory |

## Configuration

```yaml
seed: 42
number_of_companies: 100
drivers_per_company: 10
event_rate_per_driver: 3.5
company_onboarding_interval: PT1H
```

## Run Instructions

1. Launch environment: `docker compose up -d`
2. Generate companies: `docker compose exec generator python -m src.generators.company_generator --config /app/src/config/config.base.yaml --output /data/raw/companies.jsonl --seed 42`
3. Generate batch: `docker compose exec generator python -m src.generators.driver_event_generator --config /app/src/config/config.base.yaml --output /data/raw/events --companies /data/raw/companies.jsonl --now`
4. Collect metrics: Check batch_meta.json, count events, measure file sizes

## Expected Variance

- Event count: Poisson distribution implies σ = sqrt(λn) ≈ sqrt(3500) ≈ 59 events (1.7% relative variance)
- Generation time: Expected variance < 20% (depends on host resources)

## Validation

- [ ] Batch directory created under `data/raw/events/<batch_id>/`
- [ ] `events.jsonl` contains valid JSON Lines
- [ ] `batch_meta.json` records event_count, seed, interval boundaries
- [ ] Event count within ±10% of expected mean
- [ ] All timestamps fall within [interval_start, interval_end)
- [ ] Event type distribution approximately matches weights (40/35/25)

## Results

*(To be filled after experiment run)*

- **Actual generation time**: ___
- **Actual event count**: ___
- **Memory peak**: ___
- **File size**: ___
- **Pass/Fail**: ___
- **Notes**: ___
