# Medallion Pipeline (Scaffold Only)

This directory contains the scaffold for a Spark + Delta Lake medallion architecture.
No executable code is included yet.

Layers:
- bronze_ingest: Raw JSON ingestion staging (to Delta bronze)
- bronze_to_silver: Minimal transformation jobs (planned)
- silver_experiments: Variant transformation areas for iterative design
- silver_to_gold: Aggregations & curation (future)
- gold_outputs: Final curated Delta tables
- testing: Future test fixtures and expected outputs

Data storage (planned): `data/processed/medallion/{bronze|silver|gold}`.
