# Tasks: Generator Control SPA

**Input**: Design documents from `/specs/002-spa-control/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no direct dependency)
- **[Story]**: US1..US4 mapped to spec user stories
- All file paths are absolute for clarity

---
## Phase 1: Setup (Shared Infrastructure)
**Purpose**: Initialize project structure, tooling, and baseline configuration.

- [X] T001 Create frontend base directory `d:\Projects\spark-experiments\frontend` per plan
- [X] T002 Create Vite React TS project scaffold (manual setup) in `d:\Projects\spark-experiments\frontend`
- [X] T003 [P] Add `package.json` with dependencies (react, react-dom, @fluentui/react-components, axios, zod, vite, vitest, @testing-library/react)
- [X] T004 [P] Add `tsconfig.json` with strict options in `d:\Projects\spark-experiments\frontend\tsconfig.json`
- [X] T005 [P] Add `vite.config.ts` with Fluent UI optimization in `d:\Projects\spark-experiments\frontend\vite.config.ts`
- [X] T006 [P] Create `index.html` mounting root in `d:\Projects\spark-experiments\frontend\index.html`
- [X] T007 Initialize `.gitignore` additions for `frontend/dist` and node modules in `d:\Projects\spark-experiments\.gitignore`
- [X] T008 Add NPM scripts (dev, build, preview, test) to `d:\Projects\spark-experiments\frontend\package.json`
- [X] T009 Set up ESLint + Prettier baseline (optional minimal) in `d:\Projects\spark-experiments\frontend\.eslintrc.cjs`
- [X] T010 [P] Create initial `README-SPA.md` linking quickstart at `d:\Projects\spark-experiments\frontend\README-SPA.md`

---
## Phase 2: Foundational (Blocking Prerequisites)
**Purpose**: Core utilities and shared code required for all user stories.

- [ ] T011 Create shared type definitions in `d:\Projects\spark-experiments\frontend\src\state\types.ts`
- [ ] T012 [P] Implement Axios instance + interceptors in `d:\Projects\spark-experiments\frontend\src\services\apiClient.ts`
- [ ] T013 [P] Define Zod schemas for HealthSnapshot, LifecycleStatus, ControlResult, LogsResponse in `d:\Projects\spark-experiments\frontend\src\services\schemas.ts`
- [ ] T014 Implement polling hook `useInterval` in `d:\Projects\spark-experiments\frontend\src\hooks\useInterval.ts`
- [ ] T015 [P] Implement async action hook `useAsyncAction` in `d:\Projects\spark-experiments\frontend\src\hooks\useAsyncAction.ts`
- [ ] T016 Create API service modules `health.ts`, `control.ts`, `logs.ts` in `d:\Projects\spark-experiments\frontend\src\services\`
- [ ] T017 [P] Implement global error boundary component in `d:\Projects\spark-experiments\frontend\src\components\ErrorBoundary.tsx`
- [ ] T018 [P] Implement toast/notification context in `d:\Projects\spark-experiments\frontend\src\components\ToastProvider.tsx`
- [ ] T019 Add theming import and baseline Fluent UI provider in `d:\Projects\spark-experiments\frontend\src\main.tsx`
- [ ] T020 Configure environment variable access (`VITE_API_BASE`) in `d:\Projects\spark-experiments\frontend\src\services\apiClient.ts`

**Checkpoint**: All foundational utilities ready; user stories can begin independently.

---
## Phase 3: User Story 1 - Monitor Generator Health (Priority: P1) 🎯 MVP
**Goal**: Display real-time generator health (status, uptime, batch counts) auto-refreshing.
**Independent Test**: Load page; see health metrics update every ≤5s; pause state reflects correctly.

### Implementation
- [ ] T021 [P] [US1] Create `StatusBadge.tsx` in `d:\Projects\spark-experiments\frontend\src\components\StatusBadge.tsx`
- [ ] T022 [P] [US1] Create `HealthPanel.tsx` in `d:\Projects\spark-experiments\frontend\src\components\HealthPanel.tsx`
- [ ] T023 [US1] Wire health polling logic (5s interval) into `HealthPanel.tsx`
- [ ] T024 [US1] Add derived batch rate calculation inside `HealthPanel.tsx`
- [ ] T025 [US1] Add error fallback UI for health failures in `HealthPanel.tsx`
- [ ] T026 [P] [US1] Add loading skeleton state in `HealthPanel.tsx`
- [ ] T027 [US1] Integrate health + status poll staggering (5s vs 10s) in `main.tsx`
- [ ] T028 [US1] Add aria-live region for status updates in `StatusBadge.tsx`
- [ ] T029 [US1] Basic unit test for HealthPanel metrics display in `d:\Projects\spark-experiments\frontend\tests\health.spec.tsx`

**Checkpoint**: Page renders health autonomously; SC-001, SC-003 satisfied.

---
## Phase 4: User Story 2 - Pause and Resume Generation (Priority: P2)
**Goal**: Provide controls to pause/resume with confirmations and visual feedback.
**Independent Test**: Click pause → state changes to paused; click resume → returns to running; each action <2s.

### Implementation
- [ ] T030 [P] [US2] Create `ControlBar.tsx` in `d:\Projects\spark-experiments\frontend\src\components\ControlBar.tsx`
- [ ] T031 [US2] Implement pause action using `control.ts` in `ControlBar.tsx`
- [ ] T032 [US2] Implement resume action using `control.ts` in `ControlBar.tsx`
- [ ] T033 [US2] Disable buttons during in-flight requests in `ControlBar.tsx`
- [ ] T034 [US2] Show success/error toasts via `ToastProvider` in `ControlBar.tsx`
- [ ] T035 [US2] Update health/status state immediately after action completes in `main.tsx`
- [ ] T036 [P] [US2] Add unit test for pause/resume flows in `d:\Projects\spark-experiments\frontend\tests\control.spec.tsx`

**Checkpoint**: Pause/resume operable independently with feedback; SC-002, FR-006–FR-010 addressed.

---
## Phase 5: User Story 3 - View Generation Logs (Priority: P3)
**Goal**: Show recent log entries with level filtering and optional manual refresh.
**Independent Test**: Open logs view → latest entries appear; filter by level reduces list; manual refresh fetches new entries.

### Implementation
- [ ] T037 [P] [US3] Create `LogsViewer.tsx` in `d:\Projects\spark-experiments\frontend\src\components\LogsViewer.tsx`
- [ ] T038 [US3] Implement fetch & render of recent logs in `LogsViewer.tsx`
- [ ] T039 [US3] Add level filter UI (info/warning/error) in `LogsViewer.tsx`
- [ ] T040 [US3] Add manual refresh button retrieving updated logs in `LogsViewer.tsx`
- [ ] T041 [US3] Implement optional auto-refresh toggle (10s) in `LogsViewer.tsx`
- [ ] T042 [P] [US3] Add log entry truncation (>2000 chars) display logic in `LogsViewer.tsx`
- [ ] T043 [US3] Add empty state and error state UI in `LogsViewer.tsx`
- [ ] T044 [P] [US3] Unit test for filtering behavior in `d:\Projects\spark-experiments\frontend\tests\logs.spec.tsx`

**Checkpoint**: Logs accessible; FR-011–FR-015 satisfied.

---
## Phase 6: User Story 4 - Reset Data and Start Fresh (Priority: P3)
**Goal**: Provide guarded reset action only when paused; confirm and show result.
**Independent Test**: Pause → open reset dialog → confirm → data cleared (simulate success) → resume works with fresh metrics.

### Implementation
- [ ] T045 [P] [US4] Create `ResetDialog.tsx` in `d:\Projects\spark-experiments\frontend\src\components\ResetDialog.tsx`
- [ ] T046 [US4] Implement reset call (POST /clean) with guard (only if status paused) in `ResetDialog.tsx`
- [ ] T047 [US4] Add confirmation flow & destructive warning in `ResetDialog.tsx`
- [ ] T048 [US4] Display reset result (filesRemoved, durationMs) if available in `ResetDialog.tsx`
- [ ] T049 [US4] Update global state post-reset (do not auto-resume) in `main.tsx`
- [ ] T050 [US4] Unit test ensuring reset disabled while running in `d:\Projects\spark-experiments\frontend\tests\reset.spec.tsx`

**Checkpoint**: Reset workflow complete; FR-016–FR-020 satisfied.

---
## Phase 7: Docker Hosting & Integration
**Purpose**: Containerize SPA and integrate with existing docker-compose.

- [ ] T051 Create `Dockerfile.frontend` in `d:\Projects\spark-experiments\docker\Dockerfile.frontend` (multi-stage build: node → nginx)
- [ ] T052 [P] Add SPA service to `d:\Projects\spark-experiments\docker\docker-compose.yml` (e.g., service name `frontend` port 5173/80)
- [ ] T053 Configure nginx default.conf for static hosting in `d:\Projects\spark-experiments\docker\frontend.conf` (if needed)
- [ ] T054 [P] Add build instructions to `d:\Projects\spark-experiments\specs\002-spa-control\quickstart.md`
- [ ] T055 Verify CORS or same-origin alignment; adjust base URL in `d:\Projects\spark-experiments\frontend\.env`
- [ ] T056 Smoke test containerized build locally (`docker compose up frontend`) documenting results in `d:\Projects\spark-experiments\specs\002-spa-control\research.md`

**Checkpoint**: SPA served through Docker; reproducible per Constitution Principle I.

---
## Phase 8: Polish & Cross-Cutting Concerns
**Purpose**: Accessibility, performance, resilience, documentation.

- [ ] T057 Add aria-live + role attributes audit in `d:\Projects\spark-experiments\frontend\src\components`
- [ ] T058 [P] Add connection status indicator component `ConnectionStatus.tsx` in `d:\Projects\spark-experiments\frontend\src\components\ConnectionStatus.tsx`
- [ ] T059 Implement exponential backoff for failed health polls in `d:\Projects\spark-experiments\frontend\src\services\health.ts`
- [ ] T060 [P] Add bundle size check script in `d:\Projects\spark-experiments\frontend\scripts\analyze-size.mjs`
- [ ] T061 Add performance timing (initial load) log in `d:\Projects\spark-experiments\frontend\src\main.tsx`
- [ ] T062 [P] Update `README-SPA.md` with performance notes in `d:\Projects\spark-experiments\frontend\README-SPA.md`
- [ ] T063 Conduct accessibility pass and document in `d:\Projects\spark-experiments\specs\002-spa-control\research.md`
- [ ] T064 [P] Final refactor & dead code removal in `d:\Projects\spark-experiments\frontend\src\`
- [ ] T065 Validate quickstart instructions end-to-end and update `d:\Projects\spark-experiments\specs\002-spa-control\quickstart.md`

---
## Dependencies & Execution Order

### Phase Dependencies
- Setup → Foundational → User stories (US1 then others can parallel after US1 for MVP) → Docker → Polish
- US1 is MVP and must precede demo

### User Story Dependencies
- US1 independent after Foundational
- US2 depends on Foundational; can proceed parallel after US1 if health view needed for control state (soft dependency for real-time updates)
- US3 depends on Foundational (logs service) but not on US2/US4
- US4 depends on pause capability (US2) and health (US1) for guard state

### Parallel Opportunities
- Setup tasks T003–T006 can run concurrently
- Foundational tasks T012–T015–T017–T018 can parallel
- Per-story parallel tasks marked [P] (e.g., T021/T022, T030/T036, T037/T042/T044)
- Docker tasks T052/T054 may run while verifying build (T056 waits for image)

---
## Parallel Example (US1)
```
Parallel Group: T021 StatusBadge.tsx, T022 HealthPanel.tsx, T026 loading skeleton
Then: T023 polling integration, T024 derived metrics, T027 stagger logic
```

---
## Implementation Strategy
- MVP = Phases 1–3 (US1) → deploy/dev demo
- Incrementally add US2 (controls), US3 (logs), US4 (reset) → separate deploy points
- Docker integration after core value proven to minimize early complexity
- Polish last to avoid premature optimization

---
## Task Counts
- Total Tasks: 65
- Setup: 10
- Foundational: 10 (T011–T020)
- US1: 9 (T021–T029)
- US2: 7 (T030–T036)
- US3: 8 (T037–T044)
- US4: 6 (T045–T050)
- Docker Hosting: 6 (T051–T056)
- Polish: 9 (T057–T065)

Parallel tasks identified: 29

MVP Scope: Tasks T001–T029

---
## Formatting Validation
All tasks follow required format: `- [ ] T### [P?] [USX?] Description with absolute path`.

