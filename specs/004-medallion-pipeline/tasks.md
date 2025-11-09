# Tasks: Medallion Data Pipeline

## Phase 1: Setup (Shared Infrastructure)

 - [X] T001 Create feature plan file specs/004-medallion-pipeline/plan.md (minimal tech stack + directories reference)
 - [X] T002 Ensure pipeline package init file pipeline/medallion/__init__.py exists
 - [X] T003 [P] Add bronze_to_silver package init pipeline/medallion/bronze_to_silver/__init__.py
 - [X] T004 [P] Add silver_experiments package init pipeline/medallion/silver_experiments/__init__.py
 - [X] T005 [P] Add silver_to_gold package init pipeline/medallion/silver_to_gold/__init__.py
 - [X] T006 Add README verification task pipeline/medallion/README.md (confirm scaffold completeness)
 - [X] T007 Create base constants file pipeline/medallion/common/constants.py for shared paths
 - [X] T008 [P] Add utility for run timestamp pipeline/medallion/common/run_context.py

## Phase 2: Foundational (Blocking Prerequisites)

 - [X] T009 Implement schema placeholders bronze driver events pipeline/medallion/bronze_to_silver/schemas/driver_events.schema.json
 - [X] T010 [P] Implement schema placeholders bronze companies pipeline/medallion/bronze_to_silver/schemas/companies.schema.json
 - [X] T011 Implement Silver table schema placeholders pipeline/medallion/bronze_to_silver/schemas/silver_driver_events.schema.json
 - [X] T012 [P] Implement Silver companies schema placeholders pipeline/medallion/bronze_to_silver/schemas/silver_companies.schema.json
 - [X] T013 Create manifest model pipeline/medallion/common/manifest.py (ingestion + enrichment audit data classes)
 - [X] T014 Add file tracking utility pipeline/medallion/common/file_tracker.py (processed_files.json management)
 - [X] T015 [P] Add delta table writer utility pipeline/medallion/common/delta_writer.py
 - [X] T016 Create lineage metadata helper pipeline/medallion/common/lineage.py
 - [X] T017 Implement basic logging config pipeline/medallion/common/logging_config.py

## Phase 3: User Story 1 - Load Raw to Curated (Priority: P1) 🎯 MVP

Goal: Ingest raw driver events & company records into Silver with quality flags, deduplication, manifests.
Independent Test: Run ingestion on sample raw files; verify Silver tables & ingestion manifest with counts & quality flags.

### Implementation

- [ ] T018 [P] [US1] Implement ingestion entrypoint __main__ pipeline/medallion/bronze_to_silver/__main__.py (dispatch companies & events)
- [ ] T019 [P] [US1] Create driver events ingestion job pipeline/medallion/bronze_to_silver/jobs/driver_events_ingest.py
- [ ] T020 [P] [US1] Create companies ingestion job pipeline/medallion/bronze_to_silver/jobs/companies_ingest.py
- [ ] T021 [US1] Implement driver events transformation pipeline/medallion/bronze_to_silver/transformations/driver_events_transform.py
- [ ] T022 [US1] Implement companies transformation pipeline/medallion/bronze_to_silver/transformations/companies_transform.py
- [ ] T023 [US1] Add deduplication logic pipeline/medallion/bronze_to_silver/transformations/deduplicate.py
- [ ] T024 [US1] Add quality validation logic pipeline/medallion/bronze_to_silver/transformations/validation.py
- [ ] T025 [US1] Add ingestion manifest writer pipeline/medallion/bronze_to_silver/jobs/manifest_writer.py
- [ ] T026 [US1] Integrate file tracking & skip processed pipeline/medallion/bronze_to_silver/jobs/file_skip_logic.py
- [ ] T027 [US1] Wire lineage metadata injection pipeline/medallion/bronze_to_silver/jobs/lineage_injection.py
- [ ] T028 [P] [US1] Scaffold silver variant A transform placeholder pipeline/medallion/silver_experiments/variant_a/transformations/variant_a_driver_events.py
- [ ] T029 [P] [US1] Scaffold silver variant B transform placeholder pipeline/medallion/silver_experiments/variant_b/transformations/variant_b_driver_events.py

## Phase 4: User Story 2 - Enrich Driver Events (Priority: P2)

Goal: Enrich driver events with company attributes producing Gold dataset & enrichment manifest.
Independent Test: Run enrichment assuming existing Silver tables; verify Gold table & enrichment manifest metrics.

### Implementation

- [ ] T030 [P] [US2] Create enrichment entrypoint pipeline/medallion/silver_to_gold/__main__.py
- [ ] T031 [P] [US2] Create enrichment job pipeline/medallion/silver_to_gold/jobs/enrich_driver_events.py
- [ ] T032 [US2] Implement enrichment transformation pipeline/medallion/silver_to_gold/aggregations/enrich_join.py
- [ ] T033 [US2] Implement unmatched handling & threshold check pipeline/medallion/silver_to_gold/aggregations/unmatched_handling.py
- [ ] T034 [US2] Add enrichment manifest writer pipeline/medallion/silver_to_gold/jobs/enrichment_manifest_writer.py
- [ ] T035 [US2] Add delta write for Gold pipeline/medallion/silver_to_gold/jobs/gold_write.py
- [ ] T036 [P] [US2] Add lineage back-reference mapping pipeline/medallion/silver_to_gold/jobs/lineage_mapping.py

## Phase 5: User Story 3 - Provide Auditable Data Lineage (Priority: P3)

Goal: Provide manifests and lineage enabling trace from Gold back to raw source files.
Independent Test: After runs, inspect lineage query capability via helper functions mapping any Gold record to source filenames.

### Implementation

- [ ] T037 [P] [US3] Implement unified manifest schema pipeline/medallion/common/manifest_schema.py
- [ ] T038 [P] [US3] Implement lineage query helper pipeline/medallion/common/lineage_query.py
- [ ] T039 [US3] Integrate lineage query into ingestion manifest writer pipeline/medallion/bronze_to_silver/jobs/manifest_writer.py
- [ ] T040 [US3] Integrate lineage query into enrichment manifest writer pipeline/medallion/silver_to_gold/jobs/enrichment_manifest_writer.py
- [ ] T041 [US3] Add source file traceability field injection pipeline/medallion/silver_to_gold/aggregations/enrich_join.py

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T042 [P] Documentation expansion specs/004-medallion-pipeline/quickstart.md (include enrichment usage)
- [ ] T043 Refactor common validation logic pipeline/medallion/common/validation_rules.py
- [ ] T044 [P] Add performance timing wrappers pipeline/medallion/common/timing.py
- [ ] T045 Add retention cleanup script scripts/cleanup_medallion_retention.py
- [ ] T046 [P] Add deployment spark-submit script scripts/submit-medallion.ps1
- [ ] T047 Add deployment README section pipeline/medallion/README.md
- [ ] T048 Add simple integration test stub tests/integration/test_medallion_ingestion.py
- [ ] T049 [P] Add simple integration test stub tests/integration/test_medallion_enrichment.py
- [ ] T050 Final code audit & logging consistency pipeline/medallion/common/logging_config.py

## Dependencies & Execution Order

Setup → Foundational → User Stories (US1 → US2 → US3 by priority) → Polish.
Parallel tasks marked [P] can proceed after their phase prerequisites.

## Parallel Opportunities

- Package init, schema placeholders, utilities can run concurrently.
- Separate ingestion jobs (companies vs events) parallelizable.
- Variant scaffolds independent.
- Enrichment components (entrypoint, job, lineage mapping) can parallelize after US1 completes.

## MVP Scope

Complete through Phase 3 (US1) to deliver ingest & curated Silver tables + manifests.

## Summary

Total tasks: 50
User Story task counts: US1=12 (T018-T029), US2=7 (T030-T036), US3=5 (T037-T041)
Parallel tasks flagged appropriately.

