# Tasks: Driving Batch Generators

Generated on: 2025-11-08
Branch: `001-driving-batch-generators`
Spec: `specs/001-driving-batch-generators/spec.md`

## Phase 1: Setup

- [ ] T001 Initialize strict mypy config enforcement (ensure `mypy.ini` strict flags) in repo root
- [ ] T002 Add delta-spark pinned version to `requirements.txt` (confirm existing >=2.4.0)
- [ ] T003 Create `src/logging/json_logger.py` run_id field inclusion (already exists - verify, adjust if missing)
- [ ] T004 Verify Docker Compose services match spec (spark-driver, spark-executor, generator) in `docker/docker-compose.yml`
- [ ] T005 Add Makefile / PowerShell helper for common commands (optional) in repo root `Makefile`

## Phase 2: Foundational

- [ ] T006 Implement seed persistence utility in `src/util/seed.py` (exists - verify idempotency)
- [ ] T007 Add dataset descriptor writer in `src/generators/orchestrator.py` (or new file) capturing config + seed
- [ ] T008 [P] Implement batch manifest writer update logic in `src/generators/orchestrator.py`
- [ ] T009 [P] Add Poisson sampling helper in `src/generators/driver_event_generator.py`
- [ ] T010 Ensure JSON logging for discarded events with reason in `src/generators/driver_event_generator.py`

## Phase 3: User Story 1 (P1) - Company Onboarding

- [ ] T011 [US1] Add company ID generation strategy (UUID) in `src/generators/company_generator.py`
- [ ] T012 [US1] Enforce uniqueness check across runs in `src/generators/company_generator.py`
- [ ] T013 [P] [US1] Write initial companies batch if file empty in `src/generators/main.py`
- [ ] T014 [US1] Validate company schema (geography fixed US, active true) in `src/generators/company_generator.py`
- [ ] T015 [US1] Add company batch count + last time to state save logic in `src/generators/main.py`
- [ ] T016 [US1] Test: uniqueness + schema in `tests/integration/test_company_generation.py`

## Phase 4: User Story 2 (P2) - 15-Minute Driver Event Batches

- [ ] T017 [US2] Align interval computation function (15-min boundaries) in `src/generators/driver_event_generator.py`
- [ ] T018 [US2] Filter companies to those existing prior to interval_start in `src/generators/driver_event_generator.py`
- [ ] T019 [P] [US2] Generate batch_id from interval_start (ISO compact) in `src/generators/driver_event_generator.py`
- [ ] T020 [US2] Enforce timestamp boundary rule (>= start, < end) in `src/generators/driver_event_generator.py`
- [ ] T021 [US2] Create empty batch placeholder when event_count=0 in `src/generators/driver_event_generator.py`
- [ ] T022 [US2] Persist batch_meta.json with seed + counts in `src/generators/driver_event_generator.py`
- [ ] T023 [US2] Update cumulative batch manifest after each batch in `src/generators/orchestrator.py`
- [ ] T024 [US2] Test: interval alignment & boundary rule in `tests/integration/test_driver_batches.py`
- [ ] T025 [P] [US2] Test: empty interval batch placeholder in `tests/integration/test_driver_batches.py`

## Phase 5: User Story 4 (P2) - REST Runtime Control

- [ ] T026 [US4] Add lifecycle pause/resume integration checks in `src/generators/lifecycle.py` (verify existing)
- [ ] T027 [US4] Implement /pause endpoint idempotency tests in `tests/integration/test_health_routes.py`
- [ ] T028 [US4] Implement /resume endpoint idempotency tests in `tests/integration/test_health_routes.py`
- [ ] T029 [P] [US4] Add /clean precondition test (must be paused) in `tests/integration/test_health_routes.py`
- [ ] T030 [US4] Add log query filtering test for level + since in `tests/integration/test_health_logs_detailed.py`
- [ ] T031 [US4] Document curl usage (already added) confirm in `README.md`

## Phase 6: User Story 3 (P3) - Configuration Parameters

- [ ] T032 [US3] Validate config value ranges in `src/generators/config.py`
- [ ] T033 [US3] Support company_onboarding_interval ISO8601 parse in `src/generators/company_generator.py`
- [ ] T034 [P] [US3] Apply event_rate_per_driver to Poisson lambda in `src/generators/driver_event_generator.py`
- [ ] T035 [US3] Test: config change (drivers_per_company) affects batch size in `tests/integration/test_config_effects.py`
- [ ] T036 [US3] Test: onboarding interval separate cadence in `tests/integration/test_company_cadence.py`

## Phase 7: Polish & Cross-Cutting

- [ ] T037 Add mypy strict CI enforcement script in `.github/workflows/ci.yml`
- [ ] T038 [P] Add coverage threshold config to `pytest.ini` or `pyproject.toml`
- [ ] T039 Add reproducibility doc snippet to `specs/001-driving-batch-generators/quickstart.md`
- [ ] T040 [P] Optimize log parsing early-exit condition in `src/generators/health.py`
- [ ] T041 Add performance measurement scaffold (timer + metrics) in `src/generators/orchestrator.py`
- [ ] T042 [P] Add README Troubleshooting section updates (done - verify completeness)

## Dependencies / Story Order
US1 → US2 (driver events need companies) → US4 (control sits atop running system) → US3 (config extensibility) (Note: Config partly foundational; ordering chosen to deliver working core early.)

## Parallel Execution Suggestions
- Companies schema enforcement (T014) can run parallel to uniqueness test (T016) after generator skeleton.
- Batch interval alignment (T017) can run parallel to empty batch placeholder (T021) once entity model done.
- REST tests (T027-030) can run parallel to configuration tests (T035-036) after baseline endpoints exist.

## Independent Test Criteria Mapping
- US1: T016 validates uniqueness & schema.
- US2: T024/T025 validate interval boundaries & empty batch behavior.
- US3: T035/T036 validate parameter-driven scaling & onboarding cadence.
- US4: T027-T030 validate operational control & observability.

## MVP Recommendation
Implement US1 + US2 (T011–T025) for initial end-to-end dataset + batching; REST control and config scaling can follow.

## Validation
All tasks follow required checklist format with TaskID, optional [P], and [US#] labels where applicable.
---
description: "Task list for Driving Batch Generators implementation"
---

# Tasks: Driving Batch Generators

**Input**: Design documents from `/specs/001-driving-batch-generators/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Test tasks are NOT included per specification (no explicit TDD request).

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Single project structure at repository root: `src/`, `tests/`, `data/`, `experiments/`, `docker/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Docker Compose environment, project structure, and container orchestration

- [x] T001 Create project directory structure: src/generators/, src/logging/, src/util/, tests/unit/, tests/integration/, experiments/exp-001/, data/raw/, data/staged/, data/processed/, data/manifests/
- [x] T002 Create docker/docker-compose.yml with services: spark-driver (apache/spark:3.5.0), spark-executor, generator (python:3.11-slim base)
- [x] T003 [P] Add resource limits to docker-compose.yml: spark-driver (2GB mem, 1 CPU), spark-executor (2GB mem, 1 CPU), generator (512MB mem, 0.5 CPU)
- [x] T004 [P] Configure volume mounts in docker-compose.yml: ./data:/data, ./src:/app/src for generator service
- [x] T005 Create docker/Dockerfile.generator with Python 3.11-slim, install pydantic, pytest, numpy
- [x] T006 Create requirements.txt in repository root with: pydantic>=2.0, pytest>=7.0, numpy>=1.24, delta-spark==2.4.0 (for future Spark jobs)
- [x] T007 [P] Create .dockerignore to exclude: .git/, .specify/, __pycache__/, *.pyc, .pytest_cache/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T008 Create src/util/seed.py with function generate_or_load_seed(manifest_path: str, provided_seed: int | None) -> int that generates seed if absent, writes to manifest, returns seed
- [x] T009 [P] Create src/logging/json_logger.py with JSONLogger class supporting fields: timestamp (ISO8601 UTC), component (str), run_id (UUID), level (INFO/WARN/ERROR), message (str), metadata (dict)
- [x] T010 [P] Create src/generators/config.py with pydantic Config model validating: number_of_companies (int, >0), drivers_per_company (int, >0), event_rate_per_driver (float, >0), company_onboarding_interval (str, ISO8601 duration), seed (int, optional)
- [x] T011 Create src/generators/base.py with BaseGenerator abstract class providing: load_config(), setup_logging(run_id), get_seed(), write_manifest(batch_meta: dict)
- [x] T012 Create data/manifests/.gitkeep to preserve directory in version control

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Generate Company Onboarding Records (Priority: P1) 🎯 MVP

**Goal**: Produce company onboarding JSON Lines with unique IDs, fixed US geography, active status; enable coordination for driver batches

**Independent Test**: Run company generator CLI; verify companies.jsonl contains valid schema, unique company_ids, all geography='US', all active=true; verify dataset.md created

### Implementation for User Story 1

- [x] T013 [P] [US1] Create src/generators/models.py with pydantic Company model: company_id (str, UUID), geography (Literal["US"]), active (bool), created_at (datetime)
- [x] T014 [P] [US1] Create src/generators/coordination.py with function get_onboarded_companies_before(timestamp: datetime, companies_file: str) -> list[str] that reads companies.jsonl and returns company_ids created before timestamp
- [x] T015 [US1] Implement src/generators/company_generator.py inheriting BaseGenerator with generate_companies(count: int, seed: int) -> list[Company] using UUID generation
- [x] T016 [US1] Add write_companies_jsonl(companies: list[Company], output_path: str) method ensuring append-only (check existing IDs, reject duplicates, log discards)
- [x] T017 [US1] Add CLI interface to company_generator.py: argparse with --config, --output, --seed (optional), --count (optional override)
- [x] T018 [US1] Implement dataset descriptor generation: write data/manifests/dataset.md from template with seed, company_count, drivers_per_company, event_rate_per_driver, company_onboarding_interval, created_at (once on first run)
- [x] T019 [US1] Add main() orchestration: load config, get/generate seed, call generate_companies, write_companies_jsonl, write dataset descriptor if first run, log summary

**Checkpoint**: Company generator CLI functional; companies.jsonl + dataset.md written; coordination function ready for driver generator

---

## Phase 4: User Story 2 - Generate 15-Minute Driver Event Batches (Priority: P2)

**Goal**: Simulate 15-minute driver event batches with Poisson inter-arrival and weighted event_type distribution; enforce interval boundaries and company coordination

**Independent Test**: Seed companies; run driver generator with --now flag; verify events.jsonl timestamps within interval [start, end), event_count matches Poisson expectation ±10%, event_type distribution matches weights (0.40/0.35/0.25), batch_meta.json present

### Implementation for User Story 2

- [x] T020 [P] [US2] Add DriverEventRecord model to src/generators/models.py: event_id (str, UUID), driver_id (str), company_id (str), truck_id (str), event_type (Literal["start driving", "stopped driving", "delivered"]), timestamp (datetime, UTC)
- [x] T021 [P] [US2] Add DriverEventBatch model to src/generators/models.py: batch_id (str, derived from interval_start ISO compact), interval_start (datetime), interval_end (datetime), event_count (int), seed (int), generation_time (datetime)
- [x] T022 [US2] Implement src/generators/driver_event_generator.py inheriting BaseGenerator with compute_interval_bounds(now: datetime, interval_minutes: int=15) -> tuple[datetime, datetime] aligning to 15-min multiples
- [x] T023 [US2] Add generate_driver_events(companies: list[str], config: Config, interval_start: datetime, interval_end: datetime, seed: int) -> list[DriverEventRecord] using numpy.random.RandomState(seed) for Poisson(lambda=event_rate_per_driver) event counts per driver
- [x] T024 [US2] Implement weighted categorical sampling for event_type in generate_driver_events: weights=[0.40, 0.35, 0.25] for ["start driving", "stopped driving", "delivered"] using numpy.random.choice
- [x] T025 [US2] Add timestamp generation: uniform distribution within [interval_start, interval_end) for each event
- [x] T026 [US2] Add synthetic driver_id generation: pattern "DRV-{company_id}-{seq:03d}" for seq in range(drivers_per_company)
- [x] T027 [US2] Add synthetic truck_id generation: pattern "TRK-{seed}-{n:04d}" with deterministic counter
- [x] T028 [US2] Implement write_batch(events: list[DriverEventRecord], batch_meta: DriverEventBatch, output_dir: str) creating batch_id subdirectory with events.jsonl + batch_meta.json
- [x] T029 [US2] Add empty batch handling: if event_count==0, write batch_meta.json only with event_count=0
- [x] T030 [US2] Implement CLI interface: argparse with --config, --output, --interval (default 15m), --now (manual trigger), --seed (optional)
- [x] T031 [US2] Add scheduling loop in main(): if --now absent, run continuous loop: compute next interval boundary, sleep until boundary, generate batch, repeat (with graceful shutdown on SIGTERM)
- [x] T032 [US2] Integrate coordination: call get_onboarded_companies_before(interval_start) to filter eligible companies; log count of eligible vs total
- [x] T033 [US2] Update manifest: append batch summary to data/manifests/batch_manifest.json (last_batch_id, total_events accumulator, last_updated timestamp)
- [x] T034 [US2] Add discarded event logging: if truck_id missing (should not occur in generator but defensive), write to manifests/logs/discarded_events.jsonl with reason code

**Checkpoint**: Driver event generator CLI functional; produces 15-min batches with Poisson + weighted distributions; respects company coordination; manifest updated

---

## Phase 5: User Story 3 - Configure Simulation Parameters (Priority: P3)

**Goal**: Enable operator to adjust simulation scale and rates via YAML config files; validate inputs; support multiple preset configurations

**Independent Test**: Modify config.yaml to change number_of_companies to 5; run company + driver generators; verify batch event_count reflects reduced company count; test with invalid config (missing field) and verify descriptive error

### Implementation for User Story 3

- [x] T035 [P] [US3] Create src/config/config.base.yaml with: seed=42, number_of_companies=100, drivers_per_company=10, event_rate_per_driver=3.5, company_onboarding_interval="PT1H"
- [x] T036 [P] [US3] Create src/config/config.small.yaml with: seed=100, number_of_companies=5, drivers_per_company=5, event_rate_per_driver=2.0, company_onboarding_interval="PT30M"
- [x] T037 [P] [US3] Create src/config/config.scaling.yaml with: seed=200, number_of_companies=1000, drivers_per_company=20, event_rate_per_driver=5.0, company_onboarding_interval="PT2H"
- [x] T038 [US3] Add validation error handling in src/generators/config.py: catch pydantic ValidationError, format descriptive message with field name + constraint violated, exit with code 1
- [x] T039 [US3] Add config file discovery logic: if --config path not absolute, search in src/config/ then current directory; raise FileNotFoundError with helpful message if absent
- [x] T040 [US3] Update company_generator.py and driver_event_generator.py CLI help text to document config file format and example paths
- [x] T041 [US3] Add config validation test: create tests/unit/test_config_validation.py with pytest cases for missing required field, negative number_of_companies, invalid ISO8601 duration, valid config parsing

**Checkpoint**: Multiple config presets available; validation ensures safe parameter ranges; clear error messages guide operator

---

## Phase 6: Company Onboarding Cadence Coordination (Priority: P2 continuation)

**Goal**: Run company onboarding at independent hourly cadence; ensure new companies appear in driver batches only after onboarding completes

**Independent Test**: Start both generators with company_onboarding_interval=PT30M; observe company count increase at 30-min intervals; verify driver batches reference only companies onboarded before interval_start

### Implementation

- [x] T042 [US1] Add onboarding scheduling loop to company_generator.py main(): parse company_onboarding_interval from config, compute next onboarding time (align to interval), sleep until time, generate new companies batch (incremental count), repeat
- [x] T043 [US1] Implement incremental onboarding: track last onboarded count in manifests/onboarding_state.json, generate additional companies (count = number_of_companies - last_count), update state
- [x] T044 [US2] Add interval_start timestamp to driver batch coordination: pass to get_onboarded_companies_before() ensuring only companies with created_at < interval_start are included
- [x] T045 [US2] Log coordination metrics in driver_event_generator: eligible_companies_count, total_companies_count, events_generated per batch in JSON Lines

**Checkpoint**: Company onboarding runs independently; driver batches correctly exclude companies onboarded mid-interval

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple components

- [x] T046 [P] Add structured logging to all generators: log start/stop, interval boundaries, record counts, seed, duration_ms in manifests/logs/<YYYY-MM-DD>/generator.log.jsonl
- [x] T047 [P] Create experiments/exp-001/experiment.md documenting hypothesis: "Baseline batch generation completes in <5s for 5k events", metrics to collect (generation_time, event_count), expected variance
- [x] T048 [P] Copy config used for exp-001 to experiments/exp-001/config.yaml for reproducibility
- [x] T049 Add README.md in repository root with: project overview, quickstart command summary, link to specs/001-driving-batch-generators/quickstart.md
- [ ] T050 [P] Create tests/integration/test_batch_cycle.py: pytest fixture to launch generators, trigger one company onboarding + one driver batch, assert files created with correct schema and counts
- [ ] T051 Run validation per quickstart.md: docker compose up, run company generator, run driver generator --now, verify output structure matches spec
- [x] T052 Add .gitignore entries: data/*, !data/.gitkeep, !data/manifests/.gitkeep, experiments/*/metrics.jsonl, __pycache__/, .pytest_cache/, *.pyc

---

## Phase 8: Continuous Generator Container with Lifecycle Management (Priority: P2)

**Goal**: Transform generator container into long-running service that continuously generates data; implement pause/resume capability via signal handling; enable runtime control without container restart

**Independent Test**: Start generator container with continuous mode; verify companies and driver batches are generated automatically at configured intervals; send SIGUSR1 to pause generation; verify no new batches created; send SIGUSR2 to resume; verify generation resumes

### User Story 4 - Continuous Generator Service (Priority: P2)

**Why this priority**: Enables realistic simulation of continuous data flow without manual intervention; provides production-like behavior for learning objectives

**Acceptance Scenarios**:
1. **Given** generator container starts, **When** no manual trigger provided, **Then** company onboarding and driver batch generation run continuously at configured intervals
2. **Given** generator is running, **When** SIGUSR1 signal sent, **Then** generation pauses without terminating container
3. **Given** generator is paused, **When** SIGUSR2 signal sent, **Then** generation resumes from next scheduled interval

### Implementation for User Story 4

- [x] T053 [US4] Create src/generators/lifecycle.py with GeneratorLifecycle class managing pause/resume state: attributes paused (bool), should_exit (bool), pause_event (threading.Event)
- [x] T054 [P] [US4] Add signal handlers to lifecycle.py: register SIGUSR1 (pause), SIGUSR2 (resume), SIGTERM/SIGINT (graceful shutdown) with logging of state transitions
- [x] T055 [US4] Create src/generators/orchestrator.py with GeneratorOrchestrator class coordinating both company and driver generators: spawn separate threads for each generator loop, share lifecycle state
- [x] T056 [US4] Implement wait_for_next_interval(target_time: datetime, lifecycle: GeneratorLifecycle) -> bool in orchestrator.py: sleep in short intervals (1s), check pause_event and should_exit, return False if interrupted
- [x] T057 [US4] Update company_generator.py to accept --continuous flag: if present, run indefinite scheduling loop (T042 logic) with lifecycle integration; sleep using wait_for_next_interval()
- [x] T058 [US4] Update driver_event_generator.py to integrate lifecycle: check paused state before each batch generation; use wait_for_next_interval() for scheduling sleep
- [x] T059 [US4] Create src/generators/main.py as unified entry point: parse --mode (company|driver|both), initialize lifecycle, launch orchestrator threads, block on lifecycle.should_exit
- [x] T060 [US4] Add state persistence to lifecycle.py: write current state (paused, last_company_batch, last_driver_batch) to data/manifests/generator_state.json on pause and every 5 minutes
- [x] T061 [US4] Implement state recovery in main.py: on startup, read generator_state.json; if paused flag set, initialize in paused state; log recovery message
- [x] T062 [US4] Update docker/Dockerfile.generator CMD to: ["python", "-m", "src.generators.main", "--mode", "both", "--config", "/app/src/config/config.base.yaml"]
- [x] T063 [US4] Update docker-compose.yml generator service: remove "tail -f /dev/null" command override; rely on Dockerfile CMD; expose port 18000 for health endpoint; configure Spark UI ports (17080:8080, 17077:7077, 14040:4040) to avoid conflicts with commonly used ports
- [x] T064 [P] [US4] Create helper script scripts/control-generator.sh: wrapper for docker exec generator kill -SIGUSR1 (pause) and kill -SIGUSR2 (resume) with friendly messages
- [x] T065 [P] [US4] Add src/generators/health.py with simple HTTP health endpoint (port 18000, lightly used port) returning: status (running|paused), uptime, last_company_batch_time, last_driver_batch_time, batches_generated_count
- [x] T066 [US4] Update requirements.txt to add: flask>=3.0 (or fastapi if preferred for health endpoint)
- [x] T067 [US4] Add logging for lifecycle events: log PAUSE, RESUME, SHUTDOWN events with timestamp and current batch counts to manifests/logs/lifecycle.log.jsonl
- [x] T068 [US4] Update README.md with continuous mode usage: docker compose up starts continuous generation; scripts/control-generator.sh pause|resume|status for runtime control
- [ ] T069 [P] [US4] Create tests/unit/test_lifecycle.py: pytest cases for signal handling (mock signals), pause/resume state transitions, wait_for_next_interval interruption
- [ ] T070 [US4] Create tests/integration/test_continuous_generation.py: pytest fixture to start container, wait for 2 batches, send pause signal, verify no new batch in 1 min, send resume, verify batch resumes

**Checkpoint**: Generator container runs continuously; pause/resume works via signals; state persists across pause cycles; health endpoint provides observability

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **User Stories (Phase 3, 4, 5, 6)**: All depend on Foundational (Phase 2) completion
  - User Story 1 (US1) can start after Phase 2
  - User Story 2 (US2) depends on US1 coordination function (T014) but can proceed in parallel after that task
  - User Story 3 (US3) can start after Phase 2, independent of US1/US2
  - Phase 6 (onboarding cadence) extends US1 and US2, requires T015-T019 (US1) and T022-T034 (US2) complete
- **Polish (Phase 7)**: Depends on all user stories being complete
- **Phase 8 (Continuous Generator)**: Depends on Phase 6 (onboarding cadence T042-T045) and Phase 4 (driver generator T030-T031) - builds on scheduling loops

### User Story Dependencies

- **User Story 1 (US1 - Company Generator)**: Can start after Phase 2 - No dependencies on other stories
- **User Story 2 (US2 - Driver Event Generator)**: Depends on US1 coordination function (T014: get_onboarded_companies_before) - can parallelize model creation (T020, T021) with US1 work
- **User Story 3 (US3 - Config Presets)**: Can start after Phase 2 - Independent of US1/US2 (generators already consume config, just adding presets)
- **Phase 6 (Onboarding Cadence)**: Depends on US1 T015-T019 and US2 T022-T034 complete
- **User Story 4 (US4 - Continuous Generator)**: Depends on Phase 6 (T042-T045 scheduling loops) - integrates both generators into unified orchestrator

### Within Each User Story

- **US1**: T013 (models), T014 (coordination) can run in parallel → T015 (generator logic) → T016-T019 (CLI, dataset descriptor, orchestration)
- **US2**: T020, T021 (models) in parallel → T022 (interval computation) → T023-T027 (event generation, sampling, synthetic IDs) → T028-T034 (batch writing, CLI, coordination, manifest)
- **US3**: T035, T036, T037 (config files) in parallel → T038, T039 (validation logic) → T040 (docs), T041 (tests)

### Parallel Opportunities

- **Phase 1**: T003 (resource limits), T004 (volume mounts), T005 (Dockerfile), T007 (.dockerignore) can run in parallel after T002 (compose file structure)
- **Phase 2**: T009 (logging), T010 (config model), T012 (gitkeep) can run in parallel; T008 (seed utility), T011 (base generator) can follow in parallel
- **US1**: T013 (Company model), T014 (coordination function) in parallel
- **US2**: T020 (DriverEventRecord model), T021 (DriverEventBatch model) in parallel
- **US3**: T035, T036, T037 (all config files) in parallel
- **Phase 7**: T046 (logging), T047 (experiment doc), T048 (config copy), T050 (integration test), T052 (gitignore) in parallel
- **US4**: T054 (signal handlers), T064 (control script), T065 (health endpoint), T069 (lifecycle tests) can run in parallel after T053 (lifecycle class); T057 (company continuous) and T058 (driver continuous) in parallel after T056 (wait function)

---

## Parallel Example: User Story 2

```bash
# Launch model tasks together:
Task T020: "Add DriverEventRecord model to src/generators/models.py"
Task T021: "Add DriverEventBatch model to src/generators/models.py"

# After interval computation (T022), parallelize event generation components:
Task T024: "Implement weighted categorical sampling for event_type"
Task T026: "Add synthetic driver_id generation"
Task T027: "Add synthetic truck_id generation"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (Docker Compose, project structure)
2. Complete Phase 2: Foundational (config, logging, seed utility, base generator) - CRITICAL
3. Complete Phase 3: User Story 1 (company generator with coordination)
4. **STOP and VALIDATE**: Run company generator CLI, verify companies.jsonl and dataset.md created
5. Demo: Show reproducible company generation with same seed

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test company generator independently → Commit (MVP!)
3. Add User Story 2 → Test driver batch generation independently → Commit
4. Add User Story 3 → Test config presets and validation → Commit
5. Add Phase 6 → Test onboarding cadence coordination → Commit
6. Polish → Add logging, experiments, integration tests → Final commit

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup (Phase 1) + Foundational (Phase 2) together
2. Once Foundational is done:
   - Developer A: User Story 1 (company generator)
   - Developer B: User Story 3 (config presets - can start immediately)
   - Developer C: Phase 1 polish (resource limits, Dockerfile optimization)
3. After US1 T014 (coordination function) complete:
   - Developer A: Phase 6 onboarding cadence (extends US1)
   - Developer B: User Story 2 (driver event generator, uses coordination from US1)
4. Converge for Phase 7 (polish, integration tests)

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Docker Compose setup in Phase 1 enables local multi-container testing from start
- Coordination function (T014) is critical dependency for driver generator (US2)
- Poisson + weighted sampling (T023, T024) implement Option B randomness model from spec
- Port configuration uses less common ports to avoid conflicts: Spark Master UI (17080), Spark Master (17077), Spark App UI (14040), Generator Health (18000)
- Commit after each phase or logical checkpoint
- Verify generators produce valid JSON Lines matching data-model.md schemas before proceeding
- Stop at any checkpoint to validate story independently

---

## Summary

- **Total Tasks**: 70
- **Completed**: 64 tasks ✓
- **Remaining**: 6 tasks (2 tests + 2 validation + 2 integration tests)
- **User Story 1 (Company Generator)**: 7/7 tasks completed ✓ (T013-T019)
- **User Story 2 (Driver Event Generator)**: 15/15 tasks completed ✓ (T020-T034)
- **User Story 3 (Config Presets)**: 7/7 tasks completed ✓ (T035-T041)
- **User Story 4 (Continuous Generator)**: 16/18 tasks completed ✓ (T053-T068 done; T069-T070 tests pending)
- **Phase 6 (Onboarding Cadence)**: 4/4 tasks completed ✓ (T042-T045)
- **Setup + Foundational**: 12/12 tasks completed ✓ (T001-T012)
- **Polish**: 5/7 tasks completed (T046-T049, T052 done; T050-T051 pending)
- **Parallel Opportunities**: 20+ tasks can run in parallel within their phases
- **MVP Scope**: Phase 1 (Setup) + Phase 2 (Foundational) + Phase 3 (US1 Company Generator) = 19 tasks - ALL COMPLETED ✓
- **Enhanced Scope**: Phase 6 (Onboarding Cadence) + Phase 8 (Continuous Generator) = 22 tasks - 20 COMPLETED ✓
- **Production-Ready**: Continuous generation with pause/resume, state persistence, health monitoring, control scripts
- **Independent Test Criteria**: Each user story has clear standalone validation scenario

**Generated**: 2025-11-08
**Feature Branch**: 001-driving-batch-generators
**Primary Focus**: Docker Compose orchestration, Python generator coordination, Poisson + weighted randomness implementation
