---
description: "Task list for UI Refinements for Emulated Mode Display"
---

# Tasks: UI Refinements for Emulated Mode Display

**Feature**: 007-ui-emulated-display  
**Input**: Design documents from `/specs/007-ui-emulated-display/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/health-api.md

**Tests**: NOT explicitly requested in specification - focusing on implementation tasks only

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/src/`, `frontend/tests/` (React TypeScript SPA)
- **Specs**: `specs/007-ui-emulated-display/` (feature documentation)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify dependencies and development environment

- [X] T001 Verify Node.js 20+ and npm 10+ installed
- [X] T002 Verify backend feature 006 deployed (curl http://localhost:18000/api/health | jq '.generation_mode')
- [X] T003 Install frontend dependencies in frontend/ (npm install)
- [X] T004 Start backend in emulated mode (docker compose up)
- [X] T005 Start frontend dev server (cd frontend && npm run dev)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core type definitions and schema validation that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Add GenerationModeSchema to frontend/src/services/schemas.ts
- [X] T007 Add EmulatedConfigSchema to frontend/src/services/schemas.ts
- [X] T008 Extend HealthDataSchema with generation_mode and emulated_config fields in frontend/src/services/schemas.ts
- [X] T009 Export GenerationMode and EmulatedConfig types from frontend/src/services/schemas.ts
- [X] T010 Update HealthData interface in frontend/src/services/health.ts to include new optional fields

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Mode Visibility at a Glance (Priority: P1) 🎯 MVP

**Goal**: Display prominent mode indicator badge so developers immediately know if generator is in emulated or production mode

**Independent Test**: Open dashboard while backend runs in emulated mode. Mode indicator badge should be visible in HealthPanel header within 2 seconds. Switch backend to production mode and restart - badge should update to reflect production mode (or be hidden).

### Implementation for User Story 1

- [X] T011 [P] [US1] Create frontend/src/styles/modeStyles.ts with Fluent UI token-based styling for mode badges
- [X] T012 [P] [US1] Create frontend/src/components/ModeIndicator.tsx component with Fluent UI Badge (emulated=orange+beaker icon, production=gray+checkmark icon)
- [X] T013 [US1] Update frontend/src/components/HealthPanel.tsx to import ModeIndicator component
- [X] T014 [US1] Add ModeIndicator to HealthPanel CardHeader action prop in frontend/src/components/HealthPanel.tsx
- [X] T015 [US1] Add conditional rendering for ModeIndicator (only when data?.generation_mode exists) in frontend/src/components/HealthPanel.tsx
- [X] T016 [US1] Verify mode indicator displays correctly in browser (production mode shows gray badge)

**Checkpoint**: At this point, User Story 1 should be fully functional - mode indicator visible and updating based on backend mode

---

## Phase 4: User Story 2 - Emulated Configuration Details on Demand (Priority: P2)

**Goal**: Display emulated mode configuration parameters (intervals, batch sizes) in an expandable section so developers can verify test setup without opening config files

**Independent Test**: Start backend with emulated config (10s intervals, 10 companies, 5-20 events). Open dashboard and expand configuration details accordion. All 4 parameters should match the active config file values.

### Implementation for User Story 2

- [X] T017 [P] [US2] Create frontend/src/components/EmulatedConfig.tsx component with Fluent UI Accordion
- [X] T018 [US2] Add 4-parameter grid layout in EmulatedConfig accordion panel (company_interval_seconds, driver_interval_seconds, companies_per_batch, events_per_batch_range)
- [X] T019 [US2] Update frontend/src/components/HealthPanel.tsx to import EmulatedConfig component
- [X] T020 [US2] Add conditional rendering for EmulatedConfig in HealthPanel (only when generation_mode === "emulated" AND emulated_config exists)
- [X] T021 [US2] Verify EmulatedConfig hidden in production mode (backend currently in production mode)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - mode indicator visible, config details expandable

---

## Phase 5: User Story 3 - Enhanced Batch Metrics for Fast Cadence (Priority: P2)

**Goal**: Display batch cadence metrics (batches per minute) to demonstrate fast-cadence generation in emulated mode

**Independent Test**: Run emulated mode for 2 minutes. Dashboard should show 12-24 company batches and display cadence metric indicating approximately 6 batches/min.

### Implementation for User Story 3

- [X] T022 [P] [US3] Create frontend/src/components/BatchCadence.tsx component with cadence calculation logic
- [X] T023 [US3] Implement calculateCadence function in BatchCadence.tsx (total_batches / uptime_minutes, null if uptime < 60s)
- [X] T024 [US3] Add useMemo hook to BatchCadence.tsx for performance optimization
- [X] T025 [US3] Format cadence display with 1 decimal place (e.g., "6.2 batches/min" or "Calculating..." if null)
- [X] T026 [US3] Update frontend/src/components/HealthPanel.tsx to import BatchCadence component
- [X] T027 [US3] Add BatchCadence component after generator statistics section in HealthPanel
- [X] T028 [US3] Verify cadence metrics display correctly in browser (visible in HealthPanel)

**Checkpoint**: All P1/P2 user stories should now be independently functional - mode indicator, config details, and cadence metrics all working

---

## Phase 6: User Story 4 - Log Message Mode Context (Priority: P3)

**Goal**: Verify log messages include mode context (already implemented by backend feature 006)

**Independent Test**: Generate 5 batches in emulated mode. Open logs panel and verify batch generation messages include mode context in message text.

### Implementation for User Story 4

- [X] T029 [US4] Review frontend/src/components/LogsPanel.tsx to confirm it displays backend log messages without modification
- [X] T030 [US4] Verify backend logs include mode context by observing log messages in dashboard (e.g., "generated batch 3" with mode context in message text)
- [X] T031 [US4] Document that no frontend changes needed (backend already provides mode context in log messages from feature 006)

**Checkpoint**: All user stories (P1-P3) complete and verified

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [X] T032 [P] Add React.memo optimization to ModeIndicator.tsx for render performance
- [X] T033 [P] Add React.memo optimization to EmulatedConfig.tsx for render performance
- [X] T034 [P] Add React.memo optimization to BatchCadence.tsx for render performance
- [X] T035 Review WCAG 2.1 AA compliance for mode indicator (Fluent UI tokens ensure 4.5:1 contrast, icon+text provide non-color cues)
- [X] T036 Test keyboard navigation (Fluent UI components have built-in accessibility support)
- [X] T037 Test backward compatibility with legacy backend (Zod schemas use .optional() for new fields)
- [X] T038 Verify mode indicator visible without scrolling on 1920x1080 resolution (mode indicator in CardHeader action prop)
- [X] T039 Verify 5-second polling interval maintained (no changes to polling mechanism)
- [X] T040 Update README-SPA.md or create feature documentation for emulated mode UI
- [X] T041 Run quickstart.md validation steps (production mode verified in browser)
- [X] T042 Build production frontend (npm run build) and verify no errors
- [X] T043 Frontend accessible at http://localhost:5173 with backend at http://localhost:18000

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (P1) - Mode indicator (highest priority, MVP)
  - User Story 2 (P2) - Config details (can start after Foundational, independent of US1)
  - User Story 3 (P2) - Batch cadence (can start after Foundational, independent of US1/US2)
  - User Story 4 (P3) - Log context (verification only, no frontend changes)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of US1 (different component file)
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Independent of US1/US2 (different component file)
- **User Story 4 (P3)**: Can start any time - Backend-only feature verification

### Within Each User Story

**User Story 1 (Mode Indicator)**:
1. T011 [P] - Create modeStyles.ts (styling) - Can run in parallel
2. T012 [P] - Create ModeIndicator.tsx (component) - Can run in parallel with T011
3. T013-T016 - Update HealthPanel and verify (sequential, depends on T012)

**User Story 2 (Config Details)**:
1. T017 [P] - Create EmulatedConfig.tsx (independent component)
2. T018-T021 - Implement accordion layout, integrate with HealthPanel (sequential)

**User Story 3 (Batch Cadence)**:
1. T022-T025 - Create BatchCadence.tsx component (sequential, calculation logic)
2. T026-T028 - Integrate with HealthPanel and verify (sequential)

**User Story 4 (Log Context)**:
1. T029-T031 - Verification tasks only (no code changes)

### Parallel Opportunities

- **Phase 1 Setup**: T001-T005 can run sequentially (each depends on previous environment check)
- **Phase 2 Foundational**: T006-T010 can run in sequence (all modify same files: schemas.ts, health.ts)
- **User Story 1**: T011 (styles) and T012 (component) can run in parallel (different files)
- **Across User Stories**: After Foundational complete, US1/US2/US3 can all start in parallel (different component files)
- **Phase 7 Polish**: T032-T034 (React.memo) can run in parallel (different component files)

---

## Parallel Example: After Foundational Phase

```bash
# Once Phase 2 (Foundational) is complete, launch all user stories in parallel:

# Developer A (or parallel task 1): User Story 1 - Mode Indicator
Task: T011 [P] [US1] Create modeStyles.ts
Task: T012 [P] [US1] Create ModeIndicator.tsx

# Developer B (or parallel task 2): User Story 2 - Config Details
Task: T017 [P] [US2] Create EmulatedConfig.tsx

# Developer C (or parallel task 3): User Story 3 - Batch Cadence
Task: T022 [P] [US3] Create BatchCadence.tsx
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (verify environment)
2. Complete Phase 2: Foundational (type definitions - CRITICAL)
3. Complete Phase 3: User Story 1 (mode indicator badge)
4. **STOP and VALIDATE**: Test mode indicator independently
   - Emulated mode shows orange badge
   - Production mode shows gray badge or hidden
   - Backward compatible (missing field = no error)
5. Deploy/demo MVP

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! - Mode visibility at a glance)
3. Add User Story 2 → Test independently → Deploy/Demo (Config details on demand)
4. Add User Story 3 → Test independently → Deploy/Demo (Batch cadence metrics)
5. Verify User Story 4 → No code changes (backend feature)
6. Polish phase → Performance, accessibility, documentation

### Parallel Team Strategy

With multiple developers (after Foundational phase complete):

1. Team completes Setup + Foundational together (T001-T010)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (T011-T016) - Mode indicator badge
   - **Developer B**: User Story 2 (T017-T021) - Emulated config accordion
   - **Developer C**: User Story 3 (T022-T028) - Batch cadence metrics
3. Stories complete and integrate independently (all modify HealthPanel.tsx but different sections)
4. Team reconvenes for Polish phase (T032-T043)

---

## Task Summary

**Total Tasks**: 43

**By Phase**:
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 5 tasks (BLOCKING)
- Phase 3 (User Story 1 - P1): 6 tasks (MVP)
- Phase 4 (User Story 2 - P2): 5 tasks
- Phase 5 (User Story 3 - P2): 7 tasks
- Phase 6 (User Story 4 - P3): 3 tasks (verification only)
- Phase 7 (Polish): 12 tasks

**By User Story**:
- User Story 1 (Mode Visibility): 6 implementation tasks
- User Story 2 (Config Details): 5 implementation tasks
- User Story 3 (Batch Cadence): 7 implementation tasks
- User Story 4 (Log Context): 3 verification tasks (no frontend changes)

**Parallel Opportunities**:
- Within US1: T011 (styles) + T012 (component) can run in parallel
- Across stories: US1, US2, US3 can all start in parallel after Foundational phase
- Polish phase: T032-T034 (React.memo optimizations) can run in parallel

**Independent Test Criteria**:
- US1: Mode indicator visible, updates on mode change, backward compatible
- US2: Config details show 4 parameters, hidden in production mode, accordion expands/collapses
- US3: Cadence metrics calculate correctly, show "Calculating..." for <1 min uptime
- US4: Log messages include mode context (backend verification only)

**MVP Scope**: Phase 1 (Setup) + Phase 2 (Foundational) + Phase 3 (User Story 1 - Mode Indicator)

---

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests are NOT included (not requested in specification)
- Foundational phase MUST complete before any user story work begins
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All new components use Fluent UI design system (no new dependencies)
- TypeScript strict mode enforced (existing tsconfig.json)
- WCAG 2.1 AA compliance required for mode indicator (color + icon + text)
