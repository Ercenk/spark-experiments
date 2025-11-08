# Feature Specification: Clean & Auto Re-Initialization

**Feature Branch**: `003-clean-reinit`  
**Created**: 2025-11-08  
**Status**: Draft  
**Input**: User description: "Clean command on the generator service should clean all files. Upon receiving resume, it should look at the files, and if no files, should immediately generate a companies file and then a corresponding driver event file."

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

### User Story 1 - Full Data Cleanup (Priority: P1)

Operator requests a full cleanup of generated data (companies, event batches, manifests, logs) via a single action so the workspace returns to a pristine state without leftover artifacts.

**Why this priority**: Enables safe reset and prevents stale or partial datasets from polluting subsequent experiments.

**Independent Test**: Invoke cleanup on a dataset containing companies and at least one driver batch; verify all expected paths are removed and required empty directory scaffolding is recreated.

**Acceptance Scenarios**:

1. **Given** populated data folders, **When** cleanup is triggered, **Then** all generator-created files are deleted and empty required directories exist.
2. **Given** cleanup runs twice consecutively, **When** second run occurs, **Then** operation reports success without errors (idempotent) and directories remain empty.

---

### User Story 2 - Automatic Baseline Reinitialization (Priority: P2)

After cleanup, when generation is resumed, system detects absence of baseline data and immediately regenerates a fresh companies dataset and a first driver event batch without waiting for scheduled intervals.

**Why this priority**: Eliminates long idle periods (e.g., waiting an hour for company onboarding or 15 minutes for first driver batch) and accelerates iterative experimentation.

**Independent Test**: Perform cleanup; resume operation; confirm new companies file and initial driver batch appear within a short bounded time window (e.g., <5s) regardless of onboarding or batch schedule.

**Acceptance Scenarios**:

1. **Given** no companies file exists post-clean, **When** resume is issued, **Then** companies file is recreated immediately and contains the configured company count.
2. **Given** no events directory exists post-clean, **When** resume is issued, **Then** first driver batch directory (with metadata) is created immediately.
3. **Given** baseline data already exists, **When** resume is issued, **Then** no duplicate immediate regeneration occurs (only normal scheduling proceeds).

---

### User Story 3 - Reinitialization Observability (Priority: P3)

Operator can verify via status/health endpoint whether a cleanup-triggered reinitialization occurred (with timestamps and flags) to differentiate between scheduled and immediate batches.

**Why this priority**: Provides transparency and auditability of automatic regeneration events.

**Independent Test**: Perform cleanup, resume, then fetch health endpoint and confirm it contains reinit indicators and correct batch counters.

**Acceptance Scenarios**:

1. **Given** a cleanup followed by resume, **When** health is queried, **Then** response includes a flag indicating `auto_reinitialized=true` with timestamps for company and driver baseline regeneration.
2. **Given** a normal resume without preceding cleanup, **When** health is queried, **Then** response shows `auto_reinitialized=false`.

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

- Cleanup requested while already paused (allowed; proceeds normally).
- Resume issued before cleanup finishes (resume waits or fails gracefully without partial regeneration).
- Cleanup run while already empty (no error, idempotent success).
- Partial manual deletion by user (missing companies file, existing manifests) triggers only missing components regeneration.
- Race condition: concurrent resume & external file writes—system should lock or sequence operations to avoid duplicate baseline creation.
- Failure writing baseline files (disk full) → report error; do not mark reinitialized flag.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST provide a single cleanup operation that removes all generated companies, driver batch directories, manifests, logs, and dataset descriptor while recreating empty base directory structure.
- **FR-002**: Cleanup MUST be idempotent (second invocation on already cleaned state succeeds and leaves structure unchanged).
- **FR-003**: Resume operation MUST detect absence of baseline data (companies file) and trigger immediate regeneration of companies dataset.
- **FR-004**: Resume operation MUST detect absence of driver batch directory and trigger immediate creation of an initial driver batch after companies regeneration.
- **FR-005**: Immediate regeneration MUST complete within a bounded time threshold (<=5 seconds under baseline configuration) before normal scheduling continues.
- **FR-006**: System MUST avoid duplicate baseline regeneration if files already exist when resume is invoked.
- **FR-007**: Health/status endpoint MUST expose fields indicating whether automatic reinitialization occurred (`auto_reinitialized`, `reinit_company_time`, `reinit_driver_batch_id`, `reinit_driver_time`).
- **FR-008**: Automatic reinitialization MUST log a structured event including reason (missing baseline) and counts (company total, initial batch event_count).
- **FR-009**: If automatic regeneration fails (e.g., write error), system MUST surface an error flag in health/status and abstain from scheduling normal intervals until baseline is consistent.
- **FR-010**: Partial missing components (e.g., companies file present but no events directory) MUST trigger only the missing portion regeneration.
- **FR-011**: Cleanup MUST require paused state (if not paused, MUST return error instructing to pause first) while still permitting cleanup if already paused (existing behavior preserved).
- **FR-012**: Automatic regeneration MUST not overwrite existing manifest if present; it MUST recreate manifest only if missing.
- **FR-013**: System MUST maintain a counter of total auto-reinitializations for audit in health response (`auto_reinit_count`).

### Key Entities *(include if feature involves data)*

- **CleanupOperation**: timestamp, duration_ms, deleted_items[], success, error_count
- **AutoReinitEvent**: triggered_by (resume), company_count, initial_driver_batch_id, event_count, company_time, driver_time

Existing entities (Company, DriverEventBatch, BatchManifest) unchanged in schema; augmented through metadata fields exposed via status.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: Cleanup removes 100% of targeted files and completes in <3 seconds for baseline dataset (<10 companies, 1 batch).
- **SC-002**: Automatic regeneration creates companies and first driver batch in <5 seconds after resume when baseline absent.
- **SC-003**: Idempotent second cleanup reports zero deletions and success 100% of attempts.
- **SC-004**: Health endpoint reflects auto_reinitialized=true within 1 second of regeneration completion (polling scenario).
- **SC-005**: No duplicate baseline regeneration events when files are present (0 occurrences across 50 resume operations).
- **SC-006**: Partial missing component scenario regenerates only missing portion (company file untouched if present) with correctness 100%.
- **SC-007**: Auto-reinit failure surfaces error flag in health 100% of cases with failed write simulation.
