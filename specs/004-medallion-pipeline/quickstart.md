# Quickstart: Bronze to Silver Ingestion (Medallion Pipeline)

## Prerequisites
- Python 3.11
- PySpark and delta-spark (installed via `requirements.txt`)
- Raw input files present under `data/raw/events/` (JSON Lines) and optional `data/raw/companies.jsonl`

Install dependencies:
```powershell
pip install -r requirements.txt
```

## Input File Format
Driver events (JSON Lines): one JSON object per line with keys:
```json
{"driver_id":"d1","event_timestamp":"2025-11-09T00:00:00Z","event_type":"START","company_id":"c1","payload":{"k":"v"}}
```
Companies (JSON Lines):
```json
{"company_id":"c1","name":"Acme Corp","sector":"Logistics","size_indicator":"M"}
```

## Run Ingestion
Execute bronze→silver ingestion (idempotent for already processed files):
```powershell
python -m pipeline.medallion.bronze_to_silver
```

## Outputs
- Silver driver events Delta: `data/processed/silver/driver_events`
- Silver companies Delta: `data/processed/silver/companies`
- Processed file manifest: `data/manifests/processed_files.json`
- Run manifest: `data/manifests/<run_ts>/ingestion_manifest.json`

## Re-Run Behavior
- Previously ingested raw files are skipped via `processed_files.json` list.
- New files appended to Silver tables; duplicates flagged using composite key.

## Next (Enrichment)
Gold enrichment scaffold exists at `pipeline/medallion/silver_enrichment.py` and will join Silver driver events with Silver companies (implementation pending).
