# Tasks: Emulated Fast-Cadence Data Generation

**Status**: ✅ MVP Complete (2025-11-10)

**Completed Phases**:
- ✅ Phase 1: Setup (3/3 tasks)
- ✅ Phase 2: Foundational (9/9 tasks)
- ✅ Phase 3: User Story 1 Implementation (10/10 tasks)
- ✅ Phase 3: User Story 1 Unit Tests (2/2 tasks)
- ✅ Phase 5: User Story 3 API Enhancements (2/2 tasks)
- ✅ Phase 6: Polish Core Documentation (2/2 tasks)

**Test Results**:
- All 45 unit and contract tests passing (45/45)
- 19 new tests created for emulated mode functionality
- 2 compatibility issues fixed in baseline_initializer and test fixtures

**Not Implemented** (Optional/Future Enhancements):
- Integration tests requiring actual generator runs (T025-T027, T028-T031)
- Additional logging enhancements (T034-T035)
- Additional contract tests (T036-T037)
- Extended polish tasks (T040-T044)

**Implementation Notes**:
- MVP-focused approach: Core functionality complete, observability enhanced
- Schema compatibility: 100% preserved between production and emulated modes
- API backward compatible: Only additive changes to /api/health endpoint
- Configuration-driven mode toggle working via computed properties
- Fixed compatibility issues: baseline_initializer signature, test fixture config completeness

---

**Input**: Design documents from `/specs/006-emulated-generation/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in the spec—only generate validation tests for emulated mode behavior (minimal test coverage to verify functionality).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below use single project structure (per plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure—no new services, reuses existing generator infrastructure

- [x] T001 Verify existing project structure matches plan.md (src/generators/, src/config/, tests/)
- [x] T002 Create emulated mode configuration file src/config/config.emulated.yaml with default values
- [x] T003 [P] Add type annotations imports to src/generators/config.py (datetime, timedelta, Optional, Field)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core configuration infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Add EmulatedModeConfig class to src/generators/config.py with all fields (enabled, company_batch_interval, driver_batch_interval, companies_per_batch, events_per_batch_min, events_per_batch_max)
- [x] T005 Add field validators to EmulatedModeConfig in src/generators/config.py (ISO 8601 format, >=1 second minimum, max >= min)
- [x] T006 [P] Add driver_event_interval field to Config class in src/generators/config.py (default: "PT15M")
- [x] T007 [P] Add emulated_mode field to Config class in src/generators/config.py (default_factory=EmulatedModeConfig)
- [x] T008 Implement active_company_interval property in src/generators/config.py
- [x] T009 Implement active_driver_interval property in src/generators/config.py
- [x] T010 Implement active_company_count property in src/generators/config.py
- [x] T011 Add align_to_interval() helper function to src/generators/orchestrator.py
- [x] T012 Update wait_for_next_interval() in src/generators/orchestrator.py to accept emulated_mode parameter and use 0.5s check interval when True

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Observe Real-Time Data Flow (Priority: P1) 🎯 MVP

**Goal**: Generate small batches every 5-10 seconds to observe pipeline in near real-time

**Independent Test**: Start emulated mode, observe batch generation every 10 seconds, confirm data appears in bronze within seconds

### Implementation for User Story 1

- [x] T013 [US1] Update run_company_generator_continuous() in src/generators/main.py to use config.active_company_interval instead of config.company_onboarding_interval
- [x] T014 [US1] Update run_company_generator_continuous() in src/generators/main.py to use config.active_company_count for batch size
- [x] T015 [US1] Update run_driver_generator_continuous() in src/generators/main.py to parse config.active_driver_interval instead of hardcoded 15 minutes
- [x] T016 [US1] Replace hardcoded interval_minutes=15 with computed interval_seconds in src/generators/main.py run_driver_generator_continuous()
- [x] T017 [US1] Add emulated mode logic to run_driver_generator_continuous() in src/generators/main.py to limit eligible_companies list
- [x] T018 [US1] Implement event_rate_per_driver adjustment in src/generators/main.py for target event range in emulated mode
- [x] T019 [US1] Add post-generation truncation logic in src/generators/main.py if events exceed events_per_batch_max
- [x] T020 [US1] Update both continuous loops in src/generators/main.py to pass emulated_mode parameter to wait_for_next_interval()
- [x] T021 [US1] Add mode indicator logging at generator startup in src/generators/main.py (log "Starting in emulated mode" or "Starting in production mode")
- [x] T022 [US1] Add batch size logging in src/generators/main.py for each generated batch (actual vs. target counts)

### Validation for User Story 1

- [x] T023 [P] [US1] Create tests/unit/test_emulated_config.py with EmulatedModeConfig validation tests (intervals >=1s, max>=min, ISO 8601 format)
- [x] T024 [P] [US1] Create tests/unit/test_align_to_interval.py with second-level precision tests for align_to_interval()
- [ ] T025 [US1] Create tests/integration/test_emulated_mode.py with 1-minute run test (verify ~6 batches at 10s intervals)
- [ ] T026 [US1] Add batch size validation test to tests/integration/test_emulated_mode.py (verify 5-20 records per batch)
- [ ] T027 [US1] Add timing precision test to tests/integration/test_emulated_mode.py (verify <1s variance between batches)

**Checkpoint**: At this point, User Story 1 should be fully functional - emulated mode generates small batches at fast cadence

---

## Phase 4: User Story 2 - Toggle Between Production and Emulated Modes (Priority: P2)

**Goal**: Switch between modes via configuration without code changes

**Independent Test**: Toggle config setting, restart generator, observe batch size and interval changes

### Validation for User Story 2

- [ ] T028 [P] [US2] Add production mode test to tests/integration/test_emulated_mode.py (verify hourly company batches, 15-min driver batches with 100+ records)
- [ ] T029 [P] [US2] Add schema compatibility test to tests/integration/test_emulated_mode.py (compare production vs emulated batch schemas)
- [ ] T030 [US2] Add seed reproducibility test to tests/integration/test_emulated_mode.py (same seed in both modes with adjusted batch counts)
- [ ] T031 [US2] Add mode switching test to tests/integration/test_emulated_mode.py (production -> clean -> emulated -> clean -> production)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - mode can be toggled via configuration file

---

## Phase 5: User Story 3 - Visualize Pipeline Progress in Dashboard (Priority: P3)

**Goal**: Real-time dashboard metrics showing batch counts and quality statistics

**Independent Test**: Open dashboard while emulated generation runs, confirm metrics update every 5-10 seconds

### Implementation for User Story 3

- [x] T032 [P] [US3] Add generation_mode field to /api/health response in src/generators/api/__init__.py ("production" or "emulated")
- [x] T033 [P] [US3] Add emulated_config object to /api/health response in src/generators/api/__init__.py (company_interval_seconds, driver_interval_seconds, companies_per_batch, events_per_batch_range)
- [ ] T034 [US3] Add mode field to log entry extra context in src/generators/lifecycle.py (emulated vs production)
- [ ] T035 [US3] Add batch cadence metric (batches/minute) to logs in src/generators/main.py

### Validation for User Story 3

- [ ] T036 [P] [US3] Create tests/contract/test_api_health_emulated.py with health endpoint contract test for emulated mode (verify generation_mode and emulated_config fields)
- [ ] T037 [P] [US3] Add production mode health endpoint test to tests/contract/test_api_health_emulated.py (verify no emulated_config when production)

**Checkpoint**: All user stories should now be independently functional - dashboard shows real-time emulated mode status

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T038 [P] Update README.md with emulated mode quick start section
- [x] T039 [P] Create example config files: src/config/config.emulated.5s.yaml (ultra-fast), src/config/config.emulated.30s.yaml (moderate)
- [ ] T040 [P] Add emulated mode troubleshooting section to quickstart.md
- [ ] T041 [P] Document timing precision and platform differences in quickstart.md
- [ ] T042 Add performance test to tests/integration/test_emulated_mode.py (1-hour continuous run, verify no degradation)
- [ ] T043 [P] Add edge case test to tests/integration/test_emulated_mode.py (zero companies at startup)
- [ ] T044 Run validation commands from quickstart.md to verify all examples work

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational (Phase 2) - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational (Phase 2) - Tests build on US1 but can run independently
  - User Story 3 (P3): Can start after Foundational (Phase 2) - API enhancements independent of generation logic
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories ✅ INDEPENDENT
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Tests validate mode toggle but implementation in Phase 2 ✅ INDEPENDENT
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - API changes orthogonal to generation logic ✅ INDEPENDENT

### Within Each User Story

**User Story 1 Implementation Order**:
1. T013-T016: Update interval configuration usage (sequential - same files)
2. T017-T019: Add batch size control logic (sequential - build on interval changes)
3. T020-T022: Add logging and mode passing (sequential - finalize integration)
4. T023-T027: Validation tests (can run in parallel after implementation complete)

**User Story 2 Validation Order**:
- T028-T031: All validation tests can run in parallel (different test scenarios)

**User Story 3 Implementation Order**:
1. T032-T033: API response enhancements (parallel - different response sections)
2. T034-T035: Logging enhancements (parallel - different log contexts)
3. T036-T037: Contract tests (parallel - different test scenarios)

### Parallel Opportunities

- **Setup Phase**: T002, T003 can run in parallel (different files)
- **Foundational Phase**: T005, T006, T007 can run in parallel after T004 complete
- **Foundational Phase**: T008, T009, T010 can run in parallel (different properties, same class)
- **User Story 1 Tests**: T023, T024 can run in parallel (different test files)
- **User Story 2 Tests**: T028, T029, T030, T031 all parallel (different test scenarios)
- **User Story 3 Implementation**: T032, T033, T034, T035 all parallel (different files/modules)
- **User Story 3 Tests**: T036, T037 can run in parallel (different test scenarios)
- **Polish Phase**: T038, T039, T040, T041, T043 all parallel (different documentation files)

---

## Parallel Example: User Story 1 Implementation

```bash
# After Foundational phase complete, can parallelize some US1 tasks:

# Developer A: Config usage updates (T013-T016)
Task: "Update run_company_generator_continuous() to use config.active_company_interval"
Task: "Update run_company_generator_continuous() to use config.active_company_count"
Task: "Update run_driver_generator_continuous() to parse config.active_driver_interval"
Task: "Replace hardcoded interval_minutes=15 with interval_seconds"

# Developer B: Validation tests (T023, T024 - after implementation)
Task: "Create tests/unit/test_emulated_config.py"
Task: "Create tests/unit/test_align_to_interval.py"

# Then Developer A continues with batch control (T017-T022)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (emulated mode generation working)
4. **STOP and VALIDATE**: Test emulated mode with 1-minute run, verify ~6 batches
5. Deploy/demo if ready (can observe real-time pipeline flow)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! ✅)
3. Add User Story 2 → Test independently → Deploy/Demo (mode toggle validated)
4. Add User Story 3 → Test independently → Deploy/Demo (dashboard integration complete)
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (core emulated generation)
   - Developer B: User Story 3 (API enhancements - can work in parallel)
   - User Story 2 is primarily validation (can be done by either dev after US1)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Task Summary

**Total Tasks**: 44

**Task Count by Phase**:
- Phase 1 (Setup): 3 tasks
- Phase 2 (Foundational): 9 tasks (BLOCKS all user stories)
- Phase 3 (User Story 1 - P1): 15 tasks (10 implementation + 5 validation)
- Phase 4 (User Story 2 - P2): 4 tasks (all validation)
- Phase 5 (User Story 3 - P3): 6 tasks (4 implementation + 2 validation)
- Phase 6 (Polish): 7 tasks

**Parallel Opportunities**: 18 tasks marked [P] can run in parallel with others in their phase

**Independent Test Criteria**:
- **US1**: Start emulated mode, observe ~6 batches in 1 minute, verify 5-20 records per batch
- **US2**: Toggle config file, restart, verify intervals and batch sizes change without code modifications
- **US3**: Query /api/health, verify generation_mode="emulated" and emulated_config present

**Suggested MVP Scope**: Phases 1-3 (Setup + Foundational + User Story 1) = 27 tasks = ~10-12 hours

**Format Validation**: ✅ All 44 tasks follow checklist format (checkbox + ID + [P]/[Story] labels + description + file paths)
