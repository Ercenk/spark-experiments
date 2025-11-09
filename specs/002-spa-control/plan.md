# Implementation Plan: Generator Control SPA

**Branch**: `002-spa-control` | **Date**: 2025-11-08 | **Spec**: `specs/002-spa-control/spec.md`
**Input**: Feature specification from `/specs/002-spa-control/spec.md`

**Note**: Generated via `/speckit.plan`. Implementation tasks (Phase 2) will follow in `tasks.md`.

## Summary

Deliver a single-page web interface (desktop-focused) allowing operations to: (1) View real-time generator health (status, uptime, batch metrics), (2) Pause/resume all generators, (3) Perform a guarded reset while paused, (4) View recent logs with on-demand load + optional auto-refresh. Technology stack: Vite + React + TypeScript + Microsoft Fluent UI. Communication via existing generator control endpoints plus a new lightweight logs endpoint (assumed addition) that exposes recent structured JSON log entries. No persistence layer needed; all data comes from existing Python generator process. SPA kept intentionally minimal (single route) to avoid complexity creep.

## Technical Context

**Language/Version**: TypeScript 5.x (frontend), existing backend Python 3.11 (unchanged for this feature)  
**Primary Dependencies**: React 18, Vite 5, @fluentui/react-components, Axios (HTTP), Zod (runtime validation of API responses)  
**Storage**: N/A (ephemeral in-memory state only)  
**Testing**: Vitest + React Testing Library for component & contract tests; (Optional) Playwright for future E2E (deferred)  
**Target Platform**: Modern evergreen desktop browsers (Chromium, Firefox)  
**Project Type**: Web single-page application (frontend only addition)  
**Performance Goals**: Initial render < 3s (SC-001), control action round trip < 2s (SC-002), log viewport render of 500 entries < 1s  
**Constraints**: Must not add new backend services; must not violate reproducible Docker environment; minimal footprint (<150KB gzipped initial assets)  
**Scale/Scope**: Single page, 4 primary UI action groups (Health, Controls, Reset, Logs)  

Assumptions:
- Existing endpoints: `/api/health`, `/api/pause` (POST), `/api/resume` (POST), `/api/clean` (POST) already exposed by Python Flask blueprint.
- New endpoint required for logs (proposed: `GET /logs?limit=500&level=info|warning|error&since=<iso8601>`). If declined later, fallback will tail container logs via `docker logs` (NOT preferred— breaks Principle I reproducibility for automation). 
- Authentication not required (internal operator tool); if later required, wrapper proxy can enforce.
- Log entries are structured JSON lines already (from existing `json_logger`).

NEEDS CLARIFICATION (to confirm in Phase 0, currently assumed defaults):
1. Maximum log retention window the SPA should request (assumed last 10 minutes or 500 entries whichever first)
2. Whether reset should auto-resume generation after clean (assumed NO; require explicit resume) 
3. Whether partial generator failures (if in future there are multiple) should surface aggregated severity (assumed simple overall status for now)

## Constitution Check

| Principle | Risk of Violation | Assessment | Action |
|-----------|-------------------|------------|--------|
| I. Reproducible Local-First Spark Cluster | Low | Adding frontend does not modify cluster; served via dev server or static assets volume | Add build steps to README/quickstart only |
| II. Data Realism & Synthetic Fidelity | None | Read-only consumption of generator stats/logs | None |
| III. Iterative Experiment Discipline | Low | Feature isolated; no experiment directories impacted | Keep changes confined to `frontend/` |
| IV. Observability & Metrics | Positive | Increases observability surface | Ensure no removal of existing metrics |
| V. Simplicity & Teardown Hygiene | Medium | Risk of over-architecting frontend | Single-page + minimal deps + no state mgmt library |
| VI. Strict Python Type Safety | None | No new Python planned; if log endpoint added, must be fully typed | Enforce mypy on any backend change |

GATE RESULT: PASS (no blocking violations). Simplicity risk mitigated by explicit constraints (no routing library, no global state tool beyond React context/local state).

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
frontend/
  index.html
  vite.config.ts
  tsconfig.json
  src/
    main.tsx               # SPA bootstrap
    components/
      HealthPanel.tsx
      ControlBar.tsx
      ResetDialog.tsx
      LogsViewer.tsx
      StatusBadge.tsx
    services/
      apiClient.ts         # Axios instance + Zod schemas
      health.ts            # fetchHealth, fetchStatus
      control.ts           # pause, resume, reset
      logs.ts              # fetchLogs (poll or on-demand)
    hooks/
      useInterval.ts       # lightweight polling hook
      useAsyncAction.ts    # handles in-flight + errors
    state/
      types.ts             # Shared TS interfaces
    styles/
      theme.css
  tests/
    health.spec.tsx
    control.spec.tsx
    logs.spec.tsx

specs/002-spa-control/
  plan.md
  spec.md
  research.md
  data-model.md
  contracts/openapi.yaml
  quickstart.md
```

**Structure Decision**: Add isolated `frontend/` directory; no backend restructuring. Keeps Python generator untouched except optional additive logs endpoint.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|--------------------------------------|
| (none) | — | — |

## Phase 0 Plan (Research & Clarifications)

Tasks:
- Confirm assumptions for log endpoint shape & retention window.
- Decide polling vs server-sent events (choose polling for simplicity; SSE deferred).
- Determine minimal schema mapping to Zod models.
- Validate Fluent UI components needed (CommandBar, Table/List, Dialog, Toast). 

Outputs: `research.md` (decisions + rationale), purge all NEEDS CLARIFICATION items.

## Phase 1 Plan (Design & Contracts)

Deliverables:
1. `data-model.md` (Generator, HealthSnapshot, LogEntry, ControlResult, ResetResult).
2. `contracts/openapi.yaml` documenting existing + proposed `/logs` endpoint.
3. `quickstart.md` with install, dev server, build, integration steps into Docker Compose (optional static serve).
4. Update agent context to include Vite, React, Fluent UI.

## Post-Design Constitution Re-Check

Re-check summary:
| Principle | Change Since Initial | Status | Notes |
|-----------|----------------------|--------|-------|
| I | No Docker changes | PASS | Frontend isolated; optional static build only |
| II | Read-only consumption | PASS | No data generation modifications |
| III | No experiment edits | PASS | Feature separate from experiment process |
| IV | Observability improved | PASS | Added logs contract; health untouched |
| V | Simplicity preserved | PASS | Still single page; no extra state libs |
| VI | Python types unaffected | PASS | If `/logs` endpoint added, enforce strict typing + mypy before merge |

No violations introduced; complexity tracking remains empty.

## Phase 2 (Next - Not Executed Here)

Will create `tasks.md` with granular implementation tasks: scaffold project, implement services, UI components, tests, Docker integration, accessibility pass.


## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
