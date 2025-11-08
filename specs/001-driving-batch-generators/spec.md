# Feature Specification: Driving Batch Generators

**Feature Branch**: `001-driving-batch-generators`  
**Created**: 2025-11-08  
**Status**: Draft  
**Input**: User description: "we will have generators that simulate the onboarding of new customer companies and the drivers' driving records. The customer company record should have an ID, a geography, among US, EU, SA, AUS and whether they are active or not. The driver's driver record should have the company they work for, the truck they drove, the event type, e.g. start driving, stopped driving, delivered, and the timestamp. I want the records generated at fixed intervals as batches, since the trucks send their data to a central location, and that central location updates my main data store every 15 minutes. I want the generators to simulate the 15 minute data dumps."

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

### User Story 1 - Generate Company Onboarding Records (Priority: P1)

Data engineer initiates the company generator to produce onboarding records for
new transportation customer companies. Each generated company has a unique ID
and an active status. Initial iteration LIMITATION: geography is fixed to `US`
for all companies (single-geo baseline). Records are produced on initial run
and then only for newly simulated companies at a less frequent cadence (e.g.,
hourly) than driver event batches.

**Why this priority**: Foundational entity required for associating driver
events; without companies, driver batches cannot be contextualized.

**Independent Test**: Run company generator on a clean dataset; verify output
file/batch contains correct schema, unique IDs, enumerated geography values and
initial active status distribution.

**Acceptance Scenarios**:

1. **Given** no prior companies, **When** generator runs, **Then** at least one
  onboarding record per configured company count is produced with valid fields.
2. **Given** existing companies, **When** generator runs again without new
  additions, **Then** no duplicate onboarding records are produced.

---

### User Story 2 - Generate 15-Minute Driver Event Batches (Priority: P2)

System simulates trucks sending driving events (start driving, stopped driving,
delivered) which are grouped into 15-minute batches per ingestion cycle.
Each batch contains driver events referencing company ID and truck identifier.
Driver batches MUST only reference companies that existed before the start of
the interval—new companies onboarded during an interval become eligible in the
next interval.

**Why this priority**: Core ingestion learning objective—batch processing
reflects real-world periodic update pattern.

**Independent Test**: Seed a set of drivers and trucks; run generator for one
interval; validate batch file contains events only within the 15-minute window
with correct event type enumeration and timestamps.

**Acceptance Scenarios**:

1. **Given** a set of active companies and drivers, **When** the batch interval
  elapses, **Then** a batch artifact is produced containing events with
  timestamps inside that window.
2. **Given** no events occurred in an interval, **When** batch generation runs,
  **Then** an empty batch placeholder (with metadata) is produced.

---

### User Story 3 - Configure Simulation Parameters (Priority: P3)

Operator adjusts simulation parameters (number of companies, driver per company
ratio, event rate distribution, company_onboarding_interval, time zone offset
handling) via a configuration file prior to run. Geography distribution and
active toggle probability are deferred until multi-geo iteration—initial config
assumes fixed `US` geography and companies remain active (no removals yet).

**Why this priority**: Enables experimenting with scale and distribution impacts
without code changes—critical for learning Spark handling of varying batch sizes.

**Independent Test**: Modify config to change driver count and event rate;
run interval; confirm batch size and company onboarding reflect new parameters.

**Acceptance Scenarios**:

1. **Given** base configuration, **When** driver count is increased, **Then**
  subsequent batch contains proportionally more events.
2. **Given** adjusted company_onboarding_interval, **When** interval elapses,
  **Then** new companies (if any) are generated and appear only in following
  driver batches.

---

### User Story 4 - Runtime Control via REST API (Priority: P2)

Operator monitors and controls generator execution without container restarts
using REST API endpoints. System provides health monitoring (status, uptime,
batch counts, idle time), pause/resume capability, and data cleanup operations.
Health endpoint accessible at all times; pause required before cleanup to
prevent data corruption.

**Why this priority**: Enables production-like operational control; avoids
disruptive container restarts during experiments; provides observability into
generation progress.

**Independent Test**: Start generators; call GET /status to verify running state
and batch counts; call POST /pause to pause; verify no new batches generated;
call POST /resume; confirm generation resumes.

**Acceptance Scenarios**:

1. **Given** generator is running, **When** GET /health called, **Then** response
  includes status="running", uptime, batch counts, and idle time metrics.
2. **Given** generator is running, **When** POST /pause called, **Then** generation
  stops and subsequent /status shows status="paused".
3. **Given** generator is paused, **When** POST /resume called, **Then** generation
  resumes from next scheduled interval.
4. **Given** generator is paused, **When** POST /clean called, **Then** all data
  files deleted and success response returned with deleted item counts.
5. **Given** generator is running (not paused), **When** POST /clean called,
  **Then** error response returned requiring pause first.

---

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- Missing truck ID in a driver event (event discarded vs flagged).
- Company becomes inactive—(DEFERRED: no deactivation in initial iteration).
- No events in an entire hour (empty interval batches preserved).
- Overlapping timestamps on interval boundary (belongs to earlier or later batch?).
- Clock skew between simulated trucks (normalize to UTC).

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST generate onboarding records with fields: company_id (unique), geography (fixed literal `US`), active (boolean) and persist them as JSON Lines (`companies.jsonl`) in `raw/`.
- **FR-002**: System MUST ensure no duplicate company_id values across runs (append-only; duplicates rejected and logged).
- **FR-003**: System MUST produce driver event batches every 15 simulated minutes as JSON Lines (`events.jsonl`) under `raw/events/<batch_id>/` with fields: company_id, truck_id, driver_id, event_type (start driving|stopped driving|delivered), timestamp (UTC ISO8601).
- **FR-004**: System MUST include a separate batch metadata JSON (`batch_meta.json`) containing: interval_start, interval_end, event_count, seed.
- **FR-005**: System MUST create an empty batch directory with `batch_meta.json` (event_count=0) when no events occur.
- **FR-006**: System MUST read a local configuration file (YAML or JSON) specifying: number_of_companies, drivers_per_company, event_rate_per_driver, company_onboarding_interval, seed. (Geography distribution & active toggle deferred.)
- **FR-007**: System MUST validate configuration file (presence + value ranges) and abort with descriptive error if required fields missing.
- **FR-008**: System MUST normalize all timestamps to UTC regardless of local machine time zone.
- **FR-009**: (Deferred) Inactivation not supported in initial iteration; companies remain active.
- **FR-009A**: System MUST NOT remove or deactivate companies in initial iteration.
- **FR-010**: System MUST ensure each batch contains only events where timestamp >= interval_start and < interval_end (left-inclusive, right-exclusive boundary rule).
- **FR-011**: System MUST record data generation seed for reproducibility inside `batch_meta.json`.
- **FR-012**: System MUST maintain a manifest file `manifests/batch_manifest.json` with cumulative count of events and last generation time.
- **FR-013**: System MUST support manual trigger of an immediate batch via CLI flag (e.g., `--now`) without affecting schedule.
- **FR-014**: System MUST log discarded events (e.g., missing truck_id) with reason code in a JSON Lines log.
- **FR-015**: System MUST schedule company onboarding generation at a cadence independent from 15-minute driver batches (e.g., hourly configurable) using internal loop (no external API/orchestrator).
- **FR-016**: System MUST ensure driver event batches reference only companies existing before interval_start; new companies appear starting next interval.
- **FR-017**: System MUST provide REST API endpoints for runtime control: GET /health (status), GET /status (alias), POST /pause (pause generators), POST /resume (resume generators), POST /clean (clean all data).
- **FR-018**: System MUST write a dataset descriptor `manifests/dataset.md` capturing configuration snapshot and seed after first successful run.
- **FR-019**: System MUST model event generation randomness using Poisson inter-arrival (lambda derived from configured event_rate_per_driver) and weighted static probabilities for categorical attributes (event_type, active status) with weights recorded in configuration or defaults documented in data model.
- **FR-020**: System MUST automatically generate initial company batch on first startup if no companies.jsonl exists or file is empty.
- **FR-021**: System MUST expose health monitoring endpoint returning: generator status (running/paused), uptime, batch counts, last generation times, and idle durations.
- **FR-022**: System MUST require generators to be paused before allowing data cleanup via REST API.

*Assumptions: No authentication/security requirements for local experimentation; persistence mechanism abstracted (could be file-based or memory) but spec focuses on data semantics.*

### Key Entities *(include if feature involves data)*

- **Company**: company_id, geography (fixed `US`), active, created_at.
- **DriverEventRecord**: event_id, driver_id, company_id, truck_id, event_type, timestamp.
- **DriverEventBatch**: batch_id (derived from interval_start), interval_start, interval_end, event_count, seed, generation_time.
- **Config**: number_of_companies, drivers_per_company, event_rate_per_driver, company_onboarding_interval, seed.
- **BatchManifest**: manifest_id, last_batch_id, total_events, last_updated.
- **DatasetDescriptor**: seed, initial_company_count, drivers_per_company, event_rate_per_driver, company_onboarding_interval, created_at.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: Onboarding run yields 100% valid company records (schema + uniqueness) in `companies.jsonl`.
- **SC-002**: Driver batches generated exactly every 15-minute simulated interval with < 1s variance from schedule trigger.
- **SC-003**: 100% of driver events fall within correct interval boundaries (no cross-interval leakage).
- **SC-004**: Empty interval batches preserved (event_count=0) with metadata in 100% of no-event windows.
- **SC-005**: Configuration change (driver count) reflects in next batch event_count variance within ±5% of expected calculated volume.
- **SC-006**: Re-running with identical seed reproduces identical company onboarding and first interval batch contents (byte-for-byte JSON order may differ only by formatting rules; logical equivalence maintained).
- **SC-007**: Discarded events (invalid) logged with reason coverage 100% (no silent drop).
- **SC-008**: Company onboarding occurs at configured cadence (variance < 5% of scheduled time) independent from driver batch schedule.
- **SC-009**: No company removal/deactivation events appear in logs during initial iteration.
- **SC-010**: Dataset descriptor `dataset.md` written once and matches config values (100% field accuracy).
- **SC-011**: Manifest cumulative event count equals sum of all batch event_counts (consistency check passes) after each new batch.
- **SC-012**: Observed event count per 15-minute batch deviates from configured average by ≤10% (mean over 10 consecutive batches), reflecting Poisson variance.
- **SC-013**: Health endpoint responds within 100ms and returns accurate batch counts matching actual generated batches (100% accuracy).
- **SC-014**: Pause operation completes within 2 seconds and no new batches generated while paused (verified over 5-minute observation).
- **SC-015**: Resume operation completes within 2 seconds and generation resumes at next scheduled interval (no missed intervals).
- **SC-016**: Clean operation (when paused) removes 100% of specified data files and preserves directory structure.
- **SC-017**: Initial startup automatically generates company batch within 5 seconds if companies.jsonl missing or empty (100% of first-run scenarios).

## Out of Scope (Initial Iteration)

- Spark processing of JSON files into Delta or curated tables (deferred).
- Authentication/authorization for REST API endpoints.
- Company deactivation/removal lifecycle.
- Multi-geo distribution, non-US geographies.
- Advanced scheduling (external orchestrators, cron outside process).
