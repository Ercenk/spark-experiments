# Implementation Plan: SPA Styling & Operations Decoupling

**Branch**: `001-spa-styling` | **Date**: 2025-11-08 | **Spec**: `specs/001-spa-styling/spec.md`
**Input**: Feature specification from `/specs/001-spa-styling/spec.md` plus emergent need to rearchitect operational endpoints (pause/resume/clean) separate from read-only health.

**Note**: Generated via `/speckit.plan`. Operations rearchitecture will be scoped minimally inside this styling feature to avoid branching proliferation.

## Summary

Improve SPA styling (health clarity, log readability, theme persistence) and refactor backend so `health` endpoint becomes query-only while lifecycle commands (`pause`, `resume`, `clean`) move to dedicated command handlers/services. Introduce CQRS-lite separation: HealthAggregator (read) vs LifecycleCommandService (write). Add BaselineInitializer + VerificationService to ensure data generation reliability.

## Technical Context

**Language/Version**: Frontend: TypeScript 5.x + React 18; Backend: Python 3.11 (strict typing, mypy).  
**Primary Dependencies**: Frontend: Vite, @fluentui/react-components, Axios, Zod. Backend: Flask, pydantic, numpy, delta-spark (Spark runtime), internal generator modules.  
**Storage**: Ephemeral local filesystem under `/data` (raw/staged/processed). No external DB.  
**Testing**: Frontend: Vitest (unit/contract). Backend: pytest + mypy strict + integration tests hitting Flask endpoints.  
**Target Platform**: Local Docker Compose environment (Windows host, Linux containers).  
**Project Type**: Multi-part (frontend SPA + backend generator/ops service).  
**Performance Goals**: Health query p95 < 50ms locally; lifecycle command acknowledgement < 150ms; initial themed paint < 1.5s median (spec SC-006).  
**Constraints**: Must honor Constitution Principles I (Docker reproducibility), II (data fidelity), VI (strict type safety); avoid side-effects in read endpoints; no external services added.  
**Scale/Scope**: Single-operator local sandbox; anticipate dozens of health polls per minute. Concurrency minimal.  
**Unknowns (NEEDS CLARIFICATION)**:
- Optimal polling interval for health without triggering generator starvation (current guess: 2–5s).  
- Whether lifecycle commands need eventual authentication layer (out of scope now?).  
- Required OpenAPI evolution location (existing `specs/002-spa-control/contracts/openapi.yaml` vs new consolidated file).  
- Degree of Spark job awareness required in health (include metrics? future?).  
- Baseline generation retry backoff strategy.  

## Constitution Check

Principle I: Docker Compose unchanged — rearchitecture is internal Python module separation (PASS).  
Principle II: Synthetic data generation remains reproducible (PASS).  
Principle III: No experiment alteration; styling is UI feature, operations refactor internal (PASS).  
Principle IV: Health becomes pure read; improves observability clarity, but MUST still expose structured logs separately (PASS).  
Principle V: Added services increase complexity — justified by separation of concerns; will track if additional layers proliferate (FLAG: monitor).  
Principle VI: New service modules require full type annotations + mypy strict (ENFORCE).  

Gate Status: All mandatory principles satisfied; complexity addition noted for monitoring. Proceed to Phase 0.  

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
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

Selected structure: Existing `frontend/` unchanged for styling work; backend logic remains under `src/generators` but will introduce `src/generators/services/` for BaselineInitializer, VerificationService, LifecycleCommandService, HealthAggregator. Flask app will import these services; `health.py` trimmed to read-only aggregation. No additional top-level projects created.

Pending Deletions: Remove write side-effects from current `HealthServer` methods after service extraction (Phase 1). Preserve existing tests; add new ones for services.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
