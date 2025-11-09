# Data Model: SPA Styling Refinement

## Entities

### ThemePreference
- **Description**: Represents user-selected presentation mode.
- **Fields**:
  - `mode`: enum {"light", "dark"}
  - `lastChanged`: ISO timestamp string
- **Relationships**: None (isolated to client).
- **Validation Rules**: `mode` must be one of defined enum values; timestamp must parse to valid date.
- **State Transitions**:
  - `light -> dark` (user toggle)
  - `dark -> light` (user toggle)

### DesignToken
- **Description**: Abstract styling value roles available to components.
- **Fields**:
  - `color`: map { role: hex }
  - `spacing`: ordered scale array (e.g., `[0,2,4,8,12,16,24,32]`)
  - `typography`: map { tier: { fontSize, lineHeight, weight } }
- **Relationships**: Provided by Theme object referencing variants for light/dark.
- **Validation Rules**: Hex colors must match `^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$`; spacing values non-negative integers; typography tiers supply required keys.
- **State Transitions**: Immutable per theme; swapping theme replaces instance.

### StatusIndicatorModel
- **Description**: Conceptual representation for health panel entries.
- **Fields**:
  - `id`: string
  - `label`: string
  - `severity`: enum {"healthy", "degraded", "down", "unknown"}
- **Relationships**: Consumed by health panel styling functions.
- **Validation Rules**: `severity` must be defined; unknown values coerced to `"unknown"`.
- **State Transitions**:
  - Any severity may transition to any other on refresh.

## Derived Data
- **Computed Contrast Pairings**: Derived map validating color role combinations meet WCAG thresholds; cached to avoid recomputation.

## Persistence
- ThemePreference stored in `localStorage` (`app.theme`), read at bootstrap.

## Notes
No backend persistence or API schema changes required; entities remain client-scoped.
