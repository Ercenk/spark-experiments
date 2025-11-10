# Quick Start: UI Refinements for Emulated Mode Display

**Feature**: 007-ui-emulated-display  
**Created**: 2025-11-09  
**Prerequisites**: Feature 006 (emulated-generation) backend deployed

## Overview

This guide covers implementing UI enhancements to display emulated mode status, configuration details, and batch cadence metrics in the generator control dashboard.

## Prerequisites

### System Requirements
- Node.js 20+ (check: `node --version`)
- npm 10+ (check: `npm --version`)
- Backend with feature 006 deployed (provides `generation_mode` and `emulated_config` API fields)

### Dependencies (Already in package.json)
- React 18
- @fluentui/react-components
- Zod (schema validation)
- Axios (HTTP client)
- Vitest (testing)

### Optional (For Accessibility Testing)
```bash
npm install --save-dev jest-axe @axe-core/react
```

## Development Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Backend (Emulated Mode)

```bash
# In project root
docker compose up
```

**Verify backend running**:
```bash
curl http://localhost:18000/api/health | jq '.generation_mode'
# Expected: "emulated" or "production"
```

### 3. Start Frontend Dev Server

```bash
cd frontend
npm run dev
```

**Access dashboard**: http://localhost:5173

---

## Implementation Checklist

### Phase 1: Update Type Definitions (P1)

**File**: `frontend/src/services/schemas.ts`

**Add new schemas**:
```typescript
import { z } from 'zod';

export const GenerationModeSchema = z.enum(['production', 'emulated'])
  .default('production');

export const EmulatedConfigSchema = z.object({
  company_interval_seconds: z.number().positive(),
  driver_interval_seconds: z.number().positive(),
  companies_per_batch: z.number().positive().int(),
  events_per_batch_range: z.tuple([
    z.number().positive().int(),
    z.number().positive().int()
  ])
}).optional().nullable();
```

**Update HealthDataSchema**:
```typescript
export const HealthDataSchema = z.object({
  // ... existing fields
  generation_mode: GenerationModeSchema,
  emulated_config: EmulatedConfigSchema
});

export type GenerationMode = z.infer<typeof GenerationModeSchema>;
export type EmulatedConfig = z.infer<typeof EmulatedConfigSchema>;
```

**Test**: `npm test -- schemas.test.ts`

---

### Phase 2: Create ModeIndicator Component (P1 - MVP)

**File**: `frontend/src/components/ModeIndicator.tsx`

```typescript
import React from 'react';
import { Badge } from '@fluentui/react-components';
import { BeakerRegular, CheckmarkCircleRegular } from '@fluentui/react-icons';
import type { GenerationMode } from '../services/schemas';

interface ModeIndicatorProps {
  mode: GenerationMode;
}

export const ModeIndicator: React.FC<ModeIndicatorProps> = ({ mode }) => {
  if (mode === 'emulated') {
    return (
      <Badge
        color="warning"
        icon={<BeakerRegular />}
        appearance="filled"
        size="large"
      >
        Emulated Mode
      </Badge>
    );
  }
  
  return (
    <Badge
      color="subtle"
      icon={<CheckmarkCircleRegular />}
      appearance="outline"
      size="large"
    >
      Production Mode
    </Badge>
  );
};
```

**Styling**: Create `frontend/src/styles/modeStyles.ts`

```typescript
import { makeStyles, shorthands, tokens } from '@fluentui/react-components';

export const useModeStyles = makeStyles({
  emulated: {
    backgroundColor: tokens.colorPaletteYellowBackground2,
    color: tokens.colorPaletteYellowForeground1,
    ...shorthands.border('2px', 'solid', tokens.colorPaletteYellowBorder1),
    fontWeight: tokens.fontWeightSemibold,
  },
  production: {
    backgroundColor: tokens.colorNeutralBackground1,
    color: tokens.colorNeutralForeground1,
    ...shorthands.border('1px', 'solid', tokens.colorNeutralStroke1),
  },
});
```

**Test**: Create `frontend/tests/components/ModeIndicator.test.tsx`

```typescript
import { describe, test, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ModeIndicator } from '../../src/components/ModeIndicator';

describe('ModeIndicator', () => {
  test('renders emulated mode badge', () => {
    render(<ModeIndicator mode="emulated" />);
    expect(screen.getByText('Emulated Mode')).toBeInTheDocument();
  });

  test('renders production mode badge', () => {
    render(<ModeIndicator mode="production" />);
    expect(screen.getByText('Production Mode')).toBeInTheDocument();
  });
});
```

**Run tests**: `npm test -- ModeIndicator.test.tsx`

---

### Phase 3: Update HealthPanel (P1)

**File**: `frontend/src/components/HealthPanel.tsx`

**Import new components**:
```typescript
import { ModeIndicator } from './ModeIndicator';
import type { GenerationMode, EmulatedConfig } from '../services/schemas';
```

**Update interface**:
```typescript
interface HealthData {
  // ... existing fields
  generation_mode?: GenerationMode;
  emulated_config?: EmulatedConfig | null;
}
```

**Add mode indicator to render** (after CardHeader):
```typescript
<Card>
  <CardHeader
    header="Generator Health"
    action={
      data?.generation_mode && <ModeIndicator mode={data.generation_mode} />
    }
  />
  {/* ... rest of health panel */}
</Card>
```

**Verify**:
1. Start backend in emulated mode
2. Open dashboard - should see orange "Emulated Mode" badge
3. Switch backend to production - should see gray "Production Mode" badge

---

### Phase 4: Create EmulatedConfig Component (P2)

**File**: `frontend/src/components/EmulatedConfig.tsx`

```typescript
import React from 'react';
import {
  Accordion,
  AccordionHeader,
  AccordionItem,
  AccordionPanel,
} from '@fluentui/react-components';
import type { EmulatedConfig as EmulatedConfigType } from '../services/schemas';

interface EmulatedConfigProps {
  config: EmulatedConfigType;
}

export const EmulatedConfig: React.FC<EmulatedConfigProps> = ({ config }) => {
  return (
    <Accordion>
      <AccordionItem value="config">
        <AccordionHeader>Emulated Mode Configuration</AccordionHeader>
        <AccordionPanel>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
            <div>
              <strong>Company Interval:</strong> {config.company_interval_seconds}s
            </div>
            <div>
              <strong>Driver Interval:</strong> {config.driver_interval_seconds}s
            </div>
            <div>
              <strong>Companies/Batch:</strong> {config.companies_per_batch}
            </div>
            <div>
              <strong>Events/Batch:</strong> {config.events_per_batch_range[0]}-
              {config.events_per_batch_range[1]}
            </div>
          </div>
        </AccordionPanel>
      </AccordionItem>
    </Accordion>
  );
};
```

**Add to HealthPanel** (after mode indicator):
```typescript
{data?.generation_mode === 'emulated' && data?.emulated_config && (
  <EmulatedConfig config={data.emulated_config} />
)}
```

**Test**: Verify accordion expands/collapses, displays all 4 parameters

---

### Phase 5: Create BatchCadence Component (P2)

**File**: `frontend/src/components/BatchCadence.tsx`

```typescript
import React, { useMemo } from 'react';
import type { HealthData } from '../services/schemas';

interface BatchCadenceProps {
  healthData: HealthData;
}

export const BatchCadence: React.FC<BatchCadenceProps> = ({ healthData }) => {
  const cadence = useMemo(() => {
    if (healthData.uptime.seconds < 60) {
      return { company: null, driver: null };
    }
    
    const uptimeMinutes = healthData.uptime.seconds / 60;
    return {
      company: (healthData.company_generator.total_batches / uptimeMinutes).toFixed(1),
      driver: (healthData.driver_generator.total_batches / uptimeMinutes).toFixed(1),
    };
  }, [healthData]);

  if (!cadence.company || !cadence.driver) {
    return <div>Cadence: Calculating...</div>;
  }

  return (
    <div style={{ marginTop: '16px' }}>
      <div>
        <strong>Company Batches:</strong> {cadence.company} per minute
      </div>
      <div>
        <strong>Driver Batches:</strong> {cadence.driver} per minute
      </div>
    </div>
  );
};
```

**Add to HealthPanel** (after generator stats):
```typescript
<BatchCadence healthData={data} />
```

**Expected Values**:
- Emulated mode (10s intervals): ~6 batches/min
- Production mode: 0.01-4 batches/min

---

## Testing Guide

### Unit Tests

```bash
npm test
```

**Coverage**:
- ModeIndicator rendering (2 tests)
- EmulatedConfig display (1 test)
- BatchCadence calculation (3 tests: <1min, emulated, production)

### Contract Tests

```bash
npm run test:contract
```

**Tests**:
- Health API validates with new fields
- Legacy response defaults to production
- Schema validation catches invalid data

### Accessibility Tests

**Manual Checklist**:
```bash
# 1. Keyboard navigation
# - Tab to mode indicator (should focus)
# - Tab to accordion (should focus)
# - Enter/Space expands accordion

# 2. Screen reader (NVDA/JAWS)
# - Mode badge announces "Emulated Mode, badge"
# - Accordion announces "Emulated Mode Configuration, button, collapsed"

# 3. Contrast (Chrome DevTools > Inspect > Accessibility)
# - Mode badge text: 4.5:1 minimum
# - Config details: 4.5:1 minimum

# 4. High Contrast Mode (Windows)
# - Beaker icon visible
# - Border around badge visible
```

**Automated (jest-axe)**:
```typescript
import { axe, toHaveNoViolations } from 'jest-axe';
expect.extend(toHaveNoViolations);

test('ModeIndicator accessibility', async () => {
  const { container } = render(<ModeIndicator mode="emulated" />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

---

## Verification Steps

### 1. Emulated Mode Display

```bash
# Start backend in emulated mode
docker compose up

# Verify API
curl http://localhost:18000/api/health | jq '{mode: .generation_mode, config: .emulated_config}'

# Expected output:
{
  "mode": "emulated",
  "config": {
    "company_interval_seconds": 10,
    "driver_interval_seconds": 10,
    "companies_per_batch": 10,
    "events_per_batch_range": [5, 20]
  }
}
```

**Dashboard Checklist**:
- [ ] Orange "Emulated Mode" badge visible in header
- [ ] Accordion shows "Emulated Mode Configuration"
- [ ] Expanding accordion displays 4 parameters correctly
- [ ] Batch cadence shows ~6 batches/min after 1 minute

### 2. Production Mode Display

```bash
# Update backend config to production (disable emulated mode)
# Restart backend
docker compose restart

# Verify API
curl http://localhost:18000/api/health | jq '.generation_mode'
# Expected: "production"
```

**Dashboard Checklist**:
- [ ] Gray "Production Mode" badge visible (or hidden per design)
- [ ] Emulated config accordion NOT displayed
- [ ] Batch cadence shows 0.01-4 batches/min

### 3. Legacy Backend Compatibility

```bash
# Deploy frontend against older backend (without feature 006)
# Mode fields will be missing from API response
```

**Expected Behavior**:
- [ ] No mode indicator displayed (or defaults to "Production Mode")
- [ ] No emulated config section
- [ ] No errors in console
- [ ] Batch cadence still calculates correctly

---

## Common Issues

### Issue: Mode badge not appearing

**Diagnosis**:
```typescript
console.log('Health data:', data);
console.log('Mode:', data?.generation_mode);
```

**Solutions**:
- Verify backend running feature 006 (`curl http://localhost:18000/api/health | jq .generation_mode`)
- Check Zod schema allows optional mode field
- Ensure conditional render: `{data?.generation_mode && <ModeIndicator />}`

### Issue: Accordion not expanding

**Solutions**:
- Verify Fluent UI Accordion import correct
- Check browser console for React errors
- Test with `defaultExpanded={true}` prop

### Issue: Batch cadence shows "Calculating..." forever

**Diagnosis**:
```typescript
console.log('Uptime seconds:', healthData.uptime.seconds);
```

**Solutions**:
- Wait 60+ seconds after startup
- Verify uptime field present in API response
- Check calculation: `uptimeSeconds >= 60`

### Issue: Contrast ratio fails WCAG AA

**Tool**: Chrome DevTools > Inspect > Accessibility pane

**Solutions**:
- Use tokens from `@fluentui/react-components` (pre-validated)
- Test warning badge: `tokens.colorPaletteYellowForeground1` (4.5:1 contrast)
- Add explicit color overrides if needed

---

## Performance Considerations

### Polling Optimization

Current: 5-second polling (sufficient for emulated mode)

**No changes needed** unless:
- Emulated interval < 5 seconds (reduce polling to 2-3s)
- Network latency > 1 second (consider retry logic)

### Render Optimization

**Use React.memo for components**:
```typescript
export const ModeIndicator = React.memo<ModeIndicatorProps>(({ mode }) => {
  // ... component code
});
```

**Memoize cadence calculation**:
```typescript
const cadence = useMemo(() => {
  // calculation
}, [healthData.uptime.seconds, healthData.company_generator.total_batches]);
```

---

## Deployment Checklist

### Pre-Deploy
- [ ] All unit tests passing (`npm test`)
- [ ] Contract tests passing (`npm run test:contract`)
- [ ] Accessibility manual checks complete
- [ ] No console errors/warnings
- [ ] Works with emulated and production mode backends
- [ ] Works with legacy backend (missing mode fields)

### Build
```bash
npm run build
# Output: dist/
```

### Deploy (Docker)
```bash
docker compose up --build frontend
# Serves at http://localhost:19000
```

### Post-Deploy Verification
- [ ] Mode indicator visible on production deployment
- [ ] Accordion expands/collapses
- [ ] Cadence metrics update every 5 seconds
- [ ] No accessibility violations (run axe DevTools)

---

## Next Steps

After completing this feature:
1. Monitor emulated mode usage in dashboards
2. Collect feedback on cadence metric usefulness
3. Consider adding historical mode switching timeline (future enhancement)
4. Potential: Add batch size distribution charts for emulated mode analysis

---

## References

- Fluent UI React: https://react.fluentui.dev
- WCAG 2.1 Guidelines: https://www.w3.org/WAI/WCAG21/quickref/
- Zod Documentation: https://zod.dev
- Feature 006 Backend: `specs/006-emulated-generation/contracts/api-enhancements.md`
