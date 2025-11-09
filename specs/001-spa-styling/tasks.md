# Tasks: SPA Styling Refinement

**Branch**: `001-spa-styling`  
**Spec**: `specs/001-spa-styling/spec.md`  
**Plan**: `specs/001-spa-styling/plan.md`

## Dependency Graph (User Stories)
- US1 (Health styling) → Independent
- US2 (Log readability) → Independent (can start after foundational tokens)
- US3 (Theming persistence) → Independent (shares tokens infra)
- Backend Endpoint Verification (Cross-cutting) → Runs during Foundational phase

Graph: Foundational → (US1, US2, US3, US4 in parallel) → Polish

## Phase 1: Setup
- [X] T001 Initialize `frontend/src/styles/` directory structure (tokens, themes, severity) 
- [X] T002 Add placeholder `tokens.ts` file at `frontend/src/styles/tokens.ts`
- [X] T003 Add placeholder `theme.ts` file at `frontend/src/styles/theme.ts`
- [X] T004 Ensure existing service files (`frontend/src/services/health.ts`, `logs.ts`, `control.ts`) are present
- [X] T005 Create accessibility test scaffold `frontend/tests/accessibility/themeAccessibility.test.ts`

## Phase 2: Foundational (Design Tokens & Endpoint Verification)
- [X] T006 Define spacing scale & typography tiers in `frontend/src/styles/tokens.ts`
- [X] T007 Define color role palette (light + dark objects) in `frontend/src/styles/theme.ts`
- [X] T008 [P] Implement ThemeProvider wrapper in `frontend/src/main.tsx` (wrap root)
- [X] T009 Add localStorage preference read helper `frontend/src/styles/pref.ts`
- [X] T010 [P] Implement contrast validation helper `frontend/src/styles/contrast.ts`
- [X] T011 Add severity style mapping `frontend/src/styles/logSeverity.ts`
- [X] T012 Verify health endpoint usage in `frontend/src/services/health.ts` (ensure correct path & error handling)
- [X] T013 Verify logs endpoint usage in `frontend/src/services/logs.ts` (path, pagination or batch logic correctness)
- [X] T014 Verify control endpoint usage in `frontend/src/services/control.ts` (resume/pause actions correctness)
- [X] T015 Add Zod schema assertion for health response shape in `frontend/src/services/schemas.ts`
- [X] T016 [P] Add Zod schema assertion for logs payload in `frontend/src/services/schemas.ts`
- [X] T017 Add dev script note to README-SPA.md describing styling system initialization
- [X] T042 Add OpenAPI response alignment test for health `frontend/tests/contract/healthContract.test.ts`
- [X] T043 [P] Add OpenAPI response alignment test for logs `frontend/tests/contract/logsContract.test.ts`
- [X] T044 Implement pause/resume contract test `frontend/tests/contract/lifecycleContract.test.ts`
- [X] T045 Add clean endpoint contract test `frontend/tests/contract/cleanContract.test.ts`
 - [X] T046 [P] Introduce error handling wrapper for API failures `frontend/src/services/apiErrors.ts`
 - [X] T047 Add retry logic for transient log fetch errors `frontend/src/services/logs.ts` (optional exponential backoff)

## Phase 3: User Story 1 (US1 - Styled Health Overview)
- [ ] T018 [US1] Integrate tokens into `frontend/src/components/HealthPanel.tsx` (spacing, typography)
- [ ] T019 [P] [US1] Apply status color roles & iconography mapping in `HealthPanel.tsx`
- [ ] T020 [US1] Add loading skeleton component `frontend/src/components/HealthSkeleton.tsx`
- [ ] T021 [US1] Add accessibility test `frontend/tests/components/healthContrast.test.ts`
- [ ] T022 [US1] Add mock health data fixture `frontend/tests/fixtures/healthMock.json`
- [ ] T023 [US1] Implement layout stability check test `frontend/tests/components/healthLayoutShift.test.ts`
- [ ] T048 [US1] Add live fetch integration test confirming health polling renders styled states `frontend/tests/integration/healthPolling.test.ts`

## Phase 4: User Story 2 (US2 - Readable Log Consumption)
- [ ] T024 [US2] Integrate typography & spacing tokens into `frontend/src/components/LogsPanel.tsx`
- [ ] T025 [P] [US2] Apply severity mapping (border accent + weight) in `LogsPanel.tsx`
- [ ] T026 [US2] Implement long line wrap handling in `LogsPanel.tsx`
- [ ] T027 [US2] Add accessibility test for severity non-color cues `frontend/tests/components/logSeverityA11y.test.ts`
- [ ] T028 [US2] Add high-severity identification performance test scaffold `frontend/tests/perf/logScan.test.ts`
- [ ] T029 [US2] Add fixture with mixed severity logs `frontend/tests/fixtures/logsMixed.json`
- [ ] T049 [US2] Add integration test verifying log filter params map to query string `frontend/tests/integration/logsFilters.test.ts`
- [ ] T050 [US2] Implement incremental loading (pagination/since) logic in `frontend/src/components/LogsPanel.tsx`
 - [X] T098 [P] [US2] Enhance deprecated /api/logs fallback handling `frontend/src/services/logs.ts`

## Phase 5: User Story 3 (US3 - Theming & Preference Persistence)
 [X] T033 [US3] Add flicker prevention inline style injection `frontend/src/styles/injectInitialTheme.ts`

## Phase 6: User Story 4 (US4 - Responsive & Dark Mode Quality)
- [ ] T057 [US4] Define breakpoint tokens (`sm`,`md`,`lg`) in `frontend/src/styles/responsive.ts`
- [ ] T058 [P] [US4] Apply responsive container layout in `frontend/src/components/HealthPanel.tsx`
- [ ] T059 [P] [US4] Apply responsive wrapping & spacing in `frontend/src/components/LogsPanel.tsx`
- [ ] T060 [US4] Add mobile-first global stylesheet `frontend/src/styles/global.css` referenced in `frontend/src/main.tsx`
- [ ] T061 [US4] Implement viewport typography scaling helper `frontend/src/styles/typographyScale.ts`
- [ ] T062 [US4] Accessibility test no horizontal scroll @360px `frontend/tests/accessibility/responsiveNoScroll.test.ts`
- [ ] T063 [US4] Integration test breakpoint resize behavior `frontend/tests/integration/responsiveBreakpoints.test.ts`
- [ ] T064 [US4] Performance test CLS on resize `frontend/tests/perf/responsiveLayoutShift.test.ts`
- [ ] T065 [US4] Dark mode small viewport contrast test `frontend/tests/accessibility/darkModeContrastSmall.test.ts`
- [ ] T066 [US4] Update README with responsive & dark mode guidelines `frontend/README-SPA.md`
- [ ] T067 [US4] Make health skeleton responsive `frontend/src/components/HealthSkeleton.tsx`
- [ ] T068 [US4] Theme toggle dark snapshot test `frontend/tests/components/themeToggleDarkSnapshot.test.ts`
- [ ] T069 [P] [US4] Respect prefers-reduced-motion in transitions `frontend/src/styles/transitions.ts`
- [ ] T070 [US4] Add manual responsive checklist `specs/001-spa-styling/checklists/responsive.md`
 - [X] T095 [P] [US4] Synchronize html data-theme attr in ThemeProvider `frontend/src/main.tsx`
 - [X] T096 [P] [US4] Add global theming stylesheet `frontend/src/styles/global.css` and link in `frontend/index.html`
 - [X] T097 [US4] Remove partial body-only theming & ensure full viewport background via html selector `frontend/src/styles/injectInitialTheme.ts`

## Phase 7: Polish & Cross-Cutting
- [ ] T036 Add README section documenting tokens & theming guidelines `frontend/README-SPA.md`
- [ ] T037 Add axe-core integration to test setup `frontend/tests/setup/axe.ts`
- [ ] T038 [P] Add script to measure CLS & performance metrics `frontend/tests/perf/clsMeasure.test.ts`
- [ ] T039 Cleanup unused styles in components (`HealthPanel.tsx`, `LogsPanel.tsx`) removing ad-hoc values
- [ ] T040 Final contrast audit & adjustments `frontend/src/styles/theme.ts`
- [ ] T041 Prepare demo script / usage instructions `specs/001-spa-styling/demo-notes.md`
- [ ] T052 Add contract test CI grouping documentation `frontend/README-SPA.md`
- [ ] T053 [P] Add mock server harness for offline API tests `frontend/tests/setup/mockServer.ts`
- [ ] T054 Add failure simulation tests (500, timeout) `frontend/tests/contract/errorSimulation.test.ts`
- [ ] T055 Refactor services to centralize base URL & headers `frontend/src/services/apiClient.ts`
- [ ] T056 Final end-to-end sequence test (pause → resume → clean → health) `frontend/tests/integration/lifecycleFlow.test.ts`
 - [ ] T071 Fix red toast on successful reset (treat deleted_count as success) `frontend/src/services/control.ts`
 - [X] T071 Fix red toast on successful reset (treat deleted_count as success) `frontend/src/services/control.ts`
 - [ ] T072 Detect generation restart after resume (poll health, toast) `frontend/src/components/HealthPanel.tsx`
 - [ ] T073 Integration test generation restart after resume `frontend/tests/integration/resumeGeneration.test.ts`
 - [ ] T074 Verify baseline files exist after auto reinit (companies.jsonl, events/*) `src/generators/health.py`

## Phase 8: Operations Decoupling (Architecture Refactor)
- [X] T075 Create services directory `src/generators/services/` with __init__.py
- [X] T076 [P] Add baseline initializer skeleton `src/generators/services/baseline_initializer.py`
- [X] T077 [P] Add verification service skeleton `src/generators/services/verification_service.py`
- [X] T078 [P] Add lifecycle command service skeleton `src/generators/services/lifecycle_service.py`
- [X] T079 [P] Add health aggregator (read-only) `src/generators/services/health_aggregator.py`
- [X] T080 [P] Add log reader service `src/generators/services/log_reader.py`
- [X] T081 Create API blueprint package `src/generators/api/__init__.py`
- [ ] T082 [P] Add health handler module `src/generators/api/health.py`
- [ ] T083 [P] Add lifecycle handlers module (pause/resume) `src/generators/api/lifecycle.py`
- [ ] T084 [P] Add data reset handler module `src/generators/api/data_reset.py`
- [ ] T085 [P] Add logs handler module `src/generators/api/logs.py`
- [ ] T086 Document new architecture section in plan.md `specs/001-spa-styling/plan.md`
- [ ] T087 Add unit tests for baseline & verification services `tests/unit/test_services_baseline_verification.py`
- [ ] T088 Add contract test for new blueprint health endpoint `tests/contract/test_api_blueprint_health.py`
- [ ] T089 Refactor existing HealthServer to delegate to services `src/generators/health.py`
- [ ] T090 Remove write side-effects from /health endpoint (query-only) `src/generators/health.py`
 - [X] T082 [P] Add health handler module `src/generators/api/health.py`
 - [X] T083 [P] Add lifecycle handlers module (pause/resume) `src/generators/api/lifecycle.py`
 - [X] T084 [P] Add data reset handler module `src/generators/api/data_reset.py`
 - [X] T085 [P] Add logs handler module `src/generators/api/logs.py`
 - [X] T089 Refactor existing HealthServer to delegate to services `src/generators/health.py`
 - [X] T090 Remove write side-effects from /health endpoint (query-only) `src/generators/health.py`
- [ ] T091 Register blueprint in main runtime `src/generators/main.py`
 - [X] T087 Add unit tests for baseline & verification services `tests/unit/test_services_baseline_verification.py`
 - [X] T088 Add contract test for new blueprint health endpoint `tests/contract/test_api_blueprint_health.py`
 - [X] T092 Update OpenAPI with separated tags `specs/001-spa-styling/contracts/openapi.yaml`
 - [X] T093 Add quickstart section for new endpoints `specs/001-spa-styling/quickstart.md`
 - [X] T094 Add README note about migration path `frontend/README-SPA.md`
 - [X] T091 Register blueprint in main runtime `src/generators/main.py`
- [ ] T092 Update OpenAPI with separated tags `specs/001-spa-styling/contracts/openapi.yaml`
- [ ] T093 Add quickstart section for new endpoints `specs/001-spa-styling/quickstart.md`
- [ ] T094 Add README note about migration path `frontend/README-SPA.md`


## Parallel Execution Opportunities
- Tokens definition (T006, T007) precedes parallel tasks (T008, T010, T011).
- Endpoint verification tasks (T012–T016) can run alongside theme provider integration once tokens exist.
- Within each story: severity mapping tasks marked [P] can run parallel to non-dependent layout tasks.

## Independent Test Criteria Per Story
- US1: Identify system status in <10s with mock data (T021, T023).
- US2: Identify high-severity entries in <15s with mixed fixture (T027, T028).
- US3: Theme persists on reload & no flicker; contrast & focus intact (T034, T035).

## MVP Scope Recommendation
Deliver Phase 2 + US1 (Health styling) to validate token system, accessibility, and endpoint correctness before expanding to logs and theming.

## Format Validation
All tasks use required format: `- [ ] T### [P] [USn] Description with file path`. Parallel marker `[P]` only where tasks touch distinct files without dependency conflicts. Story labels applied only in story phases.

## Task Counts
- Total Tasks: 94
- Setup: 5
- Foundational: 19
- US1: 6
- US2: 9
- US3: 7
- US4: 14
- Polish: 16
- Operations Decoupling: 20

## Notes
No backend contract changes; endpoint verification ensures alignment with existing generators. Added US4 for responsiveness & enhanced dark mode quality. Adjust counts if scope evolves.
