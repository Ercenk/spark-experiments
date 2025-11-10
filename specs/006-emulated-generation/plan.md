# Implementation Plan: Emulated Fast-Cadence Data Generation

**Branch**: `006-emulated-generation` | **Date**: 2025-11-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/006-emulated-generation/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enable developers to observe complete medallion pipeline transformations in near real-time by adding emulated fast-cadence generation mode. System will generate small batches (5-20 records) at rapid intervals (5-10 seconds configurable) while preserving all production data schemas, quality injection rules, and seed-based reproducibility. Mode toggling requires only configuration changes without code modifications.

## Technical Context

**Language/Version**: Python 3.11 (existing generator codebase)
**Primary Dependencies**: Pydantic (config validation), asyncio/threading (scheduling), existing generator modules
**Storage**: JSON Lines files (existing bronze layer format)
**Testing**: pytest (existing test infrastructure)
**Target Platform**: Docker containers (Linux, existing docker-compose.yml)
**Project Type**: Single project (generator enhancements)
**Performance Goals**: Generate batches every 5-10 seconds with <1 second timing variance, sustain 1 hour continuous operation
**Constraints**: Must preserve 100% schema compatibility with production mode, zero code changes for mode switching, reuse existing quality injection framework
**Scale/Scope**: Small scope - configuration enhancements + scheduling logic changes to existing generators (company_generator.py, driver_event_generator.py, orchestrator.py)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Principle I - Reproducible Local-First Spark Cluster**: ✅ PASS
- Emulated mode runs within existing Docker Compose infrastructure
- No new containers or services required
- Configuration changes only, existing docker-compose.yml unchanged

**Principle II - Data Realism & Synthetic Fidelity**: ✅ PASS
- Preserves existing seed-based reproducibility
- Maintains identical schemas between modes
- Records generation parameters in configuration (intervals, batch sizes)
- Reuses existing quality injection framework without modification

**Principle III - Iterative Experiment Discipline**: ✅ PASS
- Emulated mode enables faster experiment iteration cycles
- No experiment directory changes required
- Supports existing hypothesis → metrics → results workflow

**Principle IV - Observability & Metrics**: ✅ PASS
- Emits same batch metadata structure as production
- Logs each batch with timestamp, size, duration
- Structured JSON Lines logging preserved
- Enables dashboard real-time metrics (US3)

**Principle V - Simplicity & Teardown Hygiene**: ✅ PASS
- Minimal complexity: configuration flag + interval/size overrides
- No new services or infrastructure
- Justification: Dramatically improves developer feedback loops (30 sec vs 15+ min)
- Teardown unchanged: `docker compose down -v` works identically

**Principle VI - Strict Python Type Safety**: ✅ PASS
- Will add type annotations for new config fields
- Existing mypy --strict enforcement continues
- New code follows PEP 484 conventions

**Principle VII - Generated Data Exclusion from Version Control**: ✅ PASS
- Generates to same `data/raw/` directories (already .gitignored)
- Only configuration files tracked (config.emulated.yaml)
- No new data directories introduced

**Constitution Check Result**: ✅ ALL PRINCIPLES PASS - No violations, proceed to Phase 0

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

```text
src/
├── generators/
│   ├── config.py              # Add emulated mode config fields
│   ├── company_generator.py   # Use emulated intervals/sizes when enabled
│   ├── driver_event_generator.py  # Use emulated intervals/sizes when enabled
│   ├── orchestrator.py        # Adapt scheduling for second-level cadence
│   ├── lifecycle.py           # Mode-aware logging
│   └── models.py              # (unchanged - schemas identical)
├── config/
│   └── config.emulated.yaml   # NEW: Emulated mode preset configuration
└── logging/                   # (unchanged)

tests/
├── integration/
│   └── test_emulated_mode.py  # NEW: Verify fast cadence + small batches
└── unit/
    └── test_emulated_config.py  # NEW: Config validation tests
```

**Structure Decision**: Single project option selected. This is a configuration and scheduling enhancement to existing generators, not a new service or application. Changes localized to generator modules with new emulated mode configuration file.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
