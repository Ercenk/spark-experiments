# Feature Specification: Medallion Data Pipeline

**Feature Branch**: `001-medallion-pipeline`  
**Created**: 2025-11-08  
**Status**: Draft  
**Input**: User description: "Build a data pipeline with medallion architecture. Initial step transfers raw to silver, then transforms and enriches driver data with company data."

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Load Raw to Curated (Priority: P1)

Operations stakeholders need reliable movement of newly arrived raw driver event files and company master data into a curated (Silver) layer with consistent schema, basic quality filters, and traceability so downstream enrichment is trustworthy.

**Why this priority**: Without clean, standardized curated data the enrichment and analytical layers cannot deliver accurate results; this is foundational for all subsequent steps.

**Independent Test**: Execute the pipeline step on an isolated sample of raw input and verify Silver outputs contain standardized columns, record counts (minus rejected), quality flags, and a load audit manifest.

**Acceptance Scenarios**:

1. **Given** new raw driver event and company source files, **When** the load job runs, **Then** Silver driver and company datasets are created with standardized schema and quality flags.
2. **Given** malformed or duplicate raw records, **When** the load job processes them, **Then** they are excluded (or flagged) and counted in a load summary.

---

### User Story 2 - Enrich Driver Events (Priority: P2)

Analysts need enriched driver event data that includes company attributes (e.g., sector, size tier) to enable segmentation and performance analysis without manual joins each time.

**Why this priority**: Adds immediate analytical value after reliable ingestion; builds upon P1 outputs.

**Independent Test**: Run enrichment step alone (assuming existing Silver inputs) and verify Gold dataset shows successful company attribute joins and retains driver event granularity.

**Acceptance Scenarios**:

1. **Given** Silver driver events and Silver company reference data, **When** enrichment runs, **Then** an enriched dataset appears containing all driver events plus company attributes for matching company ids.
2. **Given** driver events referencing missing company ids, **When** enrichment runs, **Then** those events are retained with null (or fallback) company attributes and counted in a missing reference audit.

---

### User Story 3 - Provide Auditable Data Lineage (Priority: P3)

Data governance stakeholders need visibility into when data moved between layers, how many records were accepted/rejected, and lineage back to raw source filenames to support troubleshooting and compliance.

**Why this priority**: Enhances trust and maintainability; while not required for core analytical value, it reduces operational risk.

**Independent Test**: Execute both steps and inspect generated lineage manifests showing source file names, counts, timestamps, and transformation summaries.

**Acceptance Scenarios**:

1. **Given** a completed raw→Silver load, **When** reviewing the ingestion manifest, **Then** counts of accepted/rejected driver and company records are visible with source file references.
2. **Given** an enrichment run, **When** reviewing the enrichment manifest, **Then** join match counts, unmatched company ids, and output record totals are reported.

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

- What happens when raw directory contains zero new files? (Pipeline produces no Silver changes but writes a no-op audit record.)
- How does system handle partial file writes or truncated JSON lines? (Malformed lines excluded and counted; job still succeeds.)
- What if company reference data changes between enrichment runs? (Enrichment uses latest Silver snapshot; previous Gold version retained for reproducibility.)
- How to treat duplicate driver events across multiple raw batches? (Deduplicated in Silver by composite key [event_id or timestamp+driver_id]; duplicates counted.)
- What if enrichment join rate falls below threshold (e.g., <90% matches)? (Flag raised in manifest for monitoring.)
- How does pipeline behave if a required column is missing in raw input? (Marks ingestion as failed for that file; others continue.)

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST ingest raw driver event records and company reference records into a curated Silver layer with a standardized schema and quality flags.
- **FR-002**: System MUST apply data quality rules (required fields present, valid timestamps, acceptable value ranges) and exclude or flag invalid records without aborting entire ingestion unless core schema columns are missing.
- **FR-003**: System MUST deduplicate driver events in Silver using a deterministic key (assumed composite of driver identifier + event timestamp) retaining first occurrence.
- **FR-004**: System MUST produce ingestion audit output summarizing counts: raw read, accepted, rejected (malformed, duplicates), per source file.
- **FR-005**: System MUST enrich driver events with company attributes based on company identifier, retaining unmatched events with null attributes.
- **FR-006**: System MUST produce enrichment audit metrics: total events processed, matched joins count, unmatched company ids list/count, output record count.
- **FR-007**: System MUST version outputs so prior Silver and Gold snapshots remain accessible for lineage within a defined retention window (assumed 30 days).
- **FR-008**: System MUST ensure transformations are deterministic given the same raw inputs (reruns produce identical Silver/Gold content except for timestamp metadata).
- **FR-009**: System MUST allow independent execution of ingestion and enrichment steps (enrichment only runs if Silver data present).
- **FR-010**: System MUST record start/end timestamps for each step and overall status (success, partial, failed) in a lineage manifest.
- **FR-011**: System MUST handle zero-input scenario gracefully (no failure, empty but valid audit record).
- **FR-012**: System MUST flag when enrichment match rate falls below a configurable threshold (assumed default 90%).
- **FR-013**: System MUST provide a mechanism to identify raw source file(s) for any enriched record via lineage metadata.
- **FR-014**: System MUST avoid leaking personally identifiable information in audit outputs (driver identifiers treated as non-sensitive pseudonyms for this scope).
- **FR-015**: System MUST support incremental ingestion (processing only new raw files) while preserving prior curated data.

### Key Entities *(include if feature involves data)*

- **Raw Driver Event**: A single record capturing an event produced by a driver process; attributes: driver_id, event_timestamp, event_type, payload fields, source_file_name.
- **Raw Company Record**: Company master data row; attributes: company_id, name, sector, size_indicator, source_file_name.
- **Silver Driver Event**: Cleaned, standardized driver event with quality flags (is_duplicate, is_valid), normalized types, and lineage reference.
- **Silver Company**: Curated company reference with normalized attributes and detection of field completeness.
- **Gold Enriched Driver Event**: Silver driver event augmented with company attributes (sector, size tier, etc.) and enrichment flags (company_match, join_timestamp).
- **Ingestion Audit Manifest**: Summary entity listing per-source file counts, exclusions reasons, processing timestamps.
- **Enrichment Audit Manifest**: Summary of join performance, match percentage, list/count of unmatched company ids, processing timestamps.
- **Lineage Reference**: Mapping enabling trace from Gold record back through Silver to original raw file(s).

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: Initial raw→Silver ingestion completes for typical daily volume (assumed < 1M driver events, < 10K companies) within 15 minutes wall time.
- **SC-002**: Enrichment step completes on Silver inputs within 10 minutes for same volume, producing Gold dataset matching ≥90% of driver events to a company.
- **SC-003**: Deduplication reduces duplicate driver events by ≥95% (compared to raw duplicate count) without removing unique events.
- **SC-004**: Data quality rejection rate (malformed + invalid) remains ≤5% for driver events and ≤2% for company records; breaches flagged.
- **SC-005**: Lineage query enables identification of source file for any Gold record in ≤5 seconds (lookup performance target at conceptual level).
- **SC-006**: Audit manifests are generated for 100% of successful or partial runs (no missing audit artifacts).
- **SC-007**: Re-running ingestion on identical raw inputs produces Silver outputs with ≥99.9% record-wise equivalence (excluding timestamp metadata).
- **SC-008**: Enrichment unmatched company id list completeness ≥99% (no more than 1% false negatives in missing reference reporting).
