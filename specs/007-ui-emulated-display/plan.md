# Implementation Plan: UI Refinements for Emulated Mode Display

**Branch**: `007-ui-emulated-display` | **Date**: 2025-11-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/007-ui-emulated-display/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enhance the existing React-based generator control dashboard to display emulated mode status and configuration details. Primary requirement: Add prominent mode indicator (P1), display emulated config parameters when active (P2), show batch cadence metrics (P2), and preserve mode context in logs (P3 - already implemented by backend). Technical approach: Extend existing HealthPanel component to parse new API fields (generation_mode, emulated_config), add Fluent UI Badge for mode indicator, calculate and display batches/minute metrics, maintain WCAG AA accessibility standards.

## Technical Context

**Language/Version**: TypeScript 5.x (frontend), Node.js 20+ (build tooling)
**Primary Dependencies**: React 18, Vite 5, @fluentui/react-components, Axios (HTTP), Zod (schema validation)
**Storage**: localStorage (theme preference only), no database
**Testing**: Vitest (unit tests), contract tests against live API
**Target Platform**: Modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
**Project Type**: Web application (frontend-only enhancement)
**Performance Goals**: Mode indicator visible within 2 seconds of page load, 5-second polling interval maintained, no visual jank during metric updates
**Constraints**: WCAG 2.1 AA compliance (4.5:1 contrast for normal text, non-color visual cues required), backward compatibility with production mode API (handles missing fields gracefully)
**Scale/Scope**: Single-page application, 5 existing components (HealthPanel, LogsPanel, ThemeToggle, ErrorBoundary, ToastProvider), estimated 2-3 new sub-components for mode display

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Principle I (Reproducible Local-First Spark Cluster)**: ✅ **NOT APPLICABLE** - This feature enhances frontend UI only, does not modify Docker Compose, Spark cluster configuration, or auxiliary services. Existing compose file remains unchanged.

**Principle II (Data Realism & Synthetic Fidelity)**: ✅ **NOT APPLICABLE** - No dataset generation or schema changes. Feature displays existing generator output via API.

**Principle III (Iterative Experiment Discipline)**: ✅ **NOT APPLICABLE** - No new Spark experiments. UI refinement follows standard feature development workflow (spec → plan → implement → test).

**Principle IV (Observability & Metrics)**: ✅ **COMPLIANT** - Enhances observability by surfacing generation mode and batch cadence metrics in dashboard. Log message mode context already implemented by backend (feature 006).

**Principle V (Simplicity & Teardown Hygiene)**: ✅ **COMPLIANT** - Minimal complexity added (2-3 new components for mode display, ~200-300 LOC estimated). No new services, dependencies, or infrastructure changes. Reuses existing Fluent UI design system and polling mechanism.

**Principle VI (Strict Python Type Safety)**: ✅ **NOT APPLICABLE** - TypeScript-based frontend. TypeScript strict mode already enforced in existing codebase (tsconfig.json). All new code will follow existing type safety standards.

**Principle VII (Generated Data Exclusion)**: ✅ **COMPLIANT** - No generated data artifacts. Frontend builds to `dist/` which is already .gitignored. No data files added to version control.

**Summary**: All applicable principles compliant. No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/007-ui-emulated-display/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (design patterns, accessibility)
├── data-model.md        # Phase 1 output (TypeScript interfaces)
├── quickstart.md        # Phase 1 output (developer guide)
├── contracts/           # Phase 1 output (Zod schemas for API types)
└── tasks.md             # Phase 2 output (/speckit.tasks - NOT created yet)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── components/
│   │   ├── HealthPanel.tsx          # MODIFIED: Parse generation_mode, emulated_config
│   │   ├── ModeIndicator.tsx        # NEW: P1 - Prominent mode badge
│   │   ├── EmulatedConfig.tsx       # NEW: P2 - Config details display
│   │   ├── BatchCadence.tsx         # NEW: P2 - Batches/minute metrics
│   │   ├── LogsPanel.tsx            # REVIEW: Mode context already in messages
│   │   ├── ThemeToggle.tsx          # UNCHANGED
│   │   ├── ErrorBoundary.tsx        # UNCHANGED
│   │   └── ToastProvider.tsx        # UNCHANGED
│   ├── services/
│   │   ├── health.ts                # MODIFIED: Update HealthData interface
│   │   ├── schemas.ts               # MODIFIED: Add Zod schemas for new fields
│   │   ├── apiClient.ts             # UNCHANGED
│   │   ├── apiErrors.ts             # UNCHANGED
│   │   ├── control.ts               # UNCHANGED
│   │   └── logs.ts                  # UNCHANGED
│   ├── hooks/
│   │   ├── useAsyncAction.ts        # UNCHANGED
│   │   └── useInterval.ts           # UNCHANGED
│   ├── styles/
│   │   ├── tokens.ts                # UNCHANGED (reuse existing spacing/typography)
│   │   ├── theme.ts                 # UNCHANGED (reuse theme palettes)
│   │   └── modeStyles.ts            # NEW: Mode indicator styling (colors, badges)
│   └── main.tsx                     # UNCHANGED
├── tests/
│   ├── components/
│   │   ├── ModeIndicator.test.tsx   # NEW: Mode badge rendering tests
│   │   ├── EmulatedConfig.test.tsx  # NEW: Config display tests
│   │   └── BatchCadence.test.tsx    # NEW: Metric calculation tests
│   ├── contract/
│   │   └── healthContract.test.ts   # MODIFIED: Validate new API fields
│   └── accessibility/
│       └── modeIndicator.a11y.test.tsx # NEW: WCAG AA compliance tests
├── package.json                     # REVIEW: May need a11y testing dependency
├── tsconfig.json                    # UNCHANGED
└── vite.config.ts                   # UNCHANGED
```

**Structure Decision**: Web application (Option 2) - frontend-only changes. Backend API already provides generation_mode and emulated_config fields from feature 006. No backend modifications required for this feature.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations** - Complexity tracking table not needed. All constitution principles either compliant or not applicable to frontend-only UI enhancement.
