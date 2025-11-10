# Research: UI Refinements for Emulated Mode Display

**Feature**: 007-ui-emulated-display  
**Created**: 2025-11-09  
**Status**: Complete

## Research Questions

### 1. How to implement WCAG 2.1 AA compliant mode indicators?

**Decision**: Use Fluent UI Badge component with color + icon combination

**Rationale**:
- Fluent UI Badge provides built-in accessibility features (ARIA labels, semantic HTML)
- Color alone insufficient for WCAG AA (fails for color-blind users)
- Icon + text combination provides non-color visual differentiation
- Existing project uses @fluentui/react-components - no new dependencies

**Implementation Approach**:
- Production mode: Neutral/gray badge with checkmark icon
- Emulated mode: Warning/orange badge with beaker/experiment icon
- Text always included ("Production Mode" / "Emulated Mode")
- Contrast ratio validation: 4.5:1 minimum for normal text
- Badge positioned in HealthPanel header for visibility without scrolling

**Alternatives Considered**:
- Custom styled div: Rejected - reinvents accessibility features already in Fluent UI
- Toast notifications: Rejected - ephemeral, not persistent mode indicator
- URL parameter indicator: Rejected - not visible enough, easy to miss

**References**:
- WCAG 2.1 Success Criterion 1.4.1 (Use of Color): https://www.w3.org/WAI/WCAG21/Understanding/use-of-color
- Fluent UI Badge: https://react.fluentui.dev/?path=/docs/components-badge-badge--default
- Existing theme.ts provides severity color roles with contrast helpers

---

### 2. How to calculate batch cadence (batches per minute) accurately?

**Decision**: Use total_batches / uptime_minutes with null safety

**Rationale**:
- Simple calculation, no complex state tracking required
- Data already available from existing health API (total_batches, uptime.seconds)
- Polling interval (5s) sufficient for observing emulated mode (10s batch cadence = 6/min)
- Handles zero uptime gracefully (display "—" or 0.0 when uptime < 1 minute)

**Implementation Approach**:
```typescript
function calculateCadence(totalBatches: number, uptimeSeconds: number): number | null {
  if (uptimeSeconds < 60) return null; // Not enough data
  const uptimeMinutes = uptimeSeconds / 60;
  return totalBatches / uptimeMinutes;
}
```

**Display Format**:
- First minute: Display "—" or "Calculating..." (insufficient data)
- After 1+ minutes: Display "6.2 batches/min" (1 decimal place)
- Emulated mode typical: 5-6 batches/min (10s intervals)
- Production mode: 0.01-4 batches/min (15min-1hr intervals)

**Alternatives Considered**:
- Delta tracking (batch count changes per polling cycle): Rejected - more complex, requires state management, less accurate for short windows
- Moving average window: Rejected - unnecessary complexity for MVP, current approach sufficient
- Real-time calculation via event stream: Rejected - maintains existing polling architecture

---

### 3. How to handle missing API fields gracefully (backward compatibility)?

**Decision**: Use TypeScript optional chaining and Zod schema validation with defaults

**Rationale**:
- Backend feature 006 already deployed but older backends may lack new fields
- Optional chaining (?.) prevents runtime errors when fields undefined
- Zod .optional() and .default() provide safe parsing with fallbacks
- Assume production mode when generation_mode missing (safest default)

**Implementation Approach**:
```typescript
// Zod schema
const EmulatedConfigSchema = z.object({
  company_interval_seconds: z.number(),
  driver_interval_seconds: z.number(),
  companies_per_batch: z.number(),
  events_per_batch_range: z.tuple([z.number(), z.number()])
}).optional();

const HealthDataSchema = z.object({
  // ... existing fields
  generation_mode: z.enum(['production', 'emulated']).default('production'),
  emulated_config: EmulatedConfigSchema
});

// Component rendering
{data.generation_mode === 'emulated' && data.emulated_config && (
  <EmulatedConfig config={data.emulated_config} />
)}
```

**Error Handling**:
- Missing generation_mode → assume "production", no visual indicator
- Missing emulated_config when mode="emulated" → log warning, hide config section
- Invalid field types → Zod validation fails, caught by error boundary

**Alternatives Considered**:
- Throw errors for missing fields: Rejected - breaks backward compatibility
- Version detection header: Rejected - adds API complexity, not needed for graceful degradation
- Feature detection flags: Rejected - overcomplicated for simple field presence check

---

### 4. What Fluent UI design patterns for expandable configuration details?

**Decision**: Use Fluent UI Accordion component for emulated config section

**Rationale**:
- Accordion provides expand/collapse pattern familiar to users
- Keeps HealthPanel compact by default (mode indicator visible, details on-demand)
- Existing Fluent UI component - consistent with design system
- Supports keyboard navigation (WCAG requirement)

**Implementation Approach**:
- Header: "Emulated Mode Configuration" with expand/collapse chevron
- Content: 4 parameter grid (company interval, driver interval, batch size, event range)
- Default state: Collapsed (users expand when troubleshooting)
- Persists state in component (not localStorage - ephemeral interaction)

**Layout**:
```
┌─────────────────────────────────────────┐
│ ⚗️ Emulated Mode          [ Details ▼ ] │ <- Badge + Accordion toggle
├─────────────────────────────────────────┤
│ Company Interval: 10s                   │ <- Expanded content
│ Driver Interval: 10s                    │
│ Companies/Batch: 10                     │
│ Events/Batch: 5-20                      │
└─────────────────────────────────────────┘
```

**Alternatives Considered**:
- Always-visible grid: Rejected - clutters UI when not troubleshooting
- Tooltip on hover: Rejected - not keyboard accessible, poor mobile support
- Separate modal/dialog: Rejected - too heavyweight for simple parameter display

**References**:
- Fluent UI Accordion: https://react.fluentui.dev/?path=/docs/components-accordion--default

---

### 5. How to test accessibility compliance (WCAG AA)?

**Decision**: Use axe-core + manual testing checklist

**Rationale**:
- axe-core widely adopted, integrates with Vitest via jest-axe
- Automated tests catch 30-50% of accessibility issues
- Manual checklist covers remaining requirements (keyboard nav, screen reader)
- Lightweight - no additional build complexity

**Implementation Approach**:

**Automated (jest-axe)**:
```typescript
import { axe, toHaveNoViolations } from 'jest-axe';
expect.extend(toHaveNoViolations);

test('ModeIndicator has no accessibility violations', async () => {
  const { container } = render(<ModeIndicator mode="emulated" />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

**Manual Checklist** (in quickstart.md):
1. ✅ Tab navigation reaches mode indicator
2. ✅ Screen reader announces "Emulated Mode" (ARIA label)
3. ✅ Color contrast ≥ 4.5:1 (validated via Chrome DevTools)
4. ✅ Icon visible in Windows High Contrast mode
5. ✅ Keyboard users can expand/collapse config details (Enter/Space)

**Test Coverage**:
- Unit tests: Component rendering with axe-core
- Contract tests: API field validation (ensures data available)
- Manual tests: Keyboard, screen reader, contrast (pre-merge checklist)

**Alternatives Considered**:
- Pa11y (Playwright-based): Rejected - heavier weight, slower CI runs
- Lighthouse CI: Rejected - full page audit overkill for component-level compliance
- Manual-only testing: Rejected - misses regressions, not scalable

**Dependencies**:
- `jest-axe` or `vitest-axe` (check existing test setup)
- No build changes - integrates with existing Vitest config

---

## Summary of Technical Decisions

| Aspect | Decision | Key Benefit |
|--------|----------|-------------|
| Mode Indicator | Fluent UI Badge + icon | WCAG AA compliant out-of-box |
| Cadence Calculation | total_batches / uptime_minutes | Simple, accurate, no state management |
| Backward Compatibility | Zod optional chaining + defaults | Graceful degradation for old backends |
| Config Details | Fluent UI Accordion | Compact by default, accessible expand/collapse |
| Accessibility Testing | axe-core + manual checklist | Automated + human validation coverage |

## Dependencies & Best Practices

**No New Dependencies Required**:
- @fluentui/react-components (already in package.json)
- Zod (already in package.json)
- Vitest (already in package.json)
- Optional: jest-axe or vitest-axe (check if already available, add if needed)

**Existing Patterns to Follow**:
- Token-based styling (src/styles/tokens.ts for spacing/typography)
- Theme-aware components (src/styles/theme.ts for color palettes)
- Zod schema validation (src/services/schemas.ts pattern)
- Polling architecture (existing useInterval hook, 5s interval)
- Error boundary pattern (existing ErrorBoundary.tsx)

**Performance Considerations**:
- Batch cadence calculated on every render - memoize with useMemo if needed
- Mode indicator renders once per health poll (5s) - negligible overhead
- Accordion expand/collapse pure client-side (no API calls)

## Open Questions Resolved

All research questions resolved. No blocking unknowns remain. Ready to proceed to Phase 1 (data-model.md, contracts/, quickstart.md).
