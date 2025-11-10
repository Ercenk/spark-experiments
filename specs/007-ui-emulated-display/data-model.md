# Data Model: UI Refinements for Emulated Mode Display

**Feature**: 007-ui-emulated-display  
**Created**: 2025-11-09  
**Status**: Design

## Overview

This feature extends existing frontend data models to support emulated mode display. All types are TypeScript interfaces consumed by React components. No database or persistent storage involved - data sourced from /api/health endpoint.

## Type Definitions

### GenerationMode (Enum)

Represents the current operating mode of the data generator.

**TypeScript Definition**:
```typescript
export type GenerationMode = 'production' | 'emulated';
```

**Values**:
- `production`: Standard mode with hourly company batches, 15-minute driver batches
- `emulated`: Fast-cadence mode with 5-10 second intervals for rapid observation

**Validation**: Zod enum with default fallback to 'production'

**Usage**: Displayed in mode indicator badge, determines visibility of emulated config section

---

### EmulatedConfig (Object)

Configuration parameters active when generation_mode is "emulated".

**TypeScript Definition**:
```typescript
export interface EmulatedConfig {
  company_interval_seconds: number;      // Batch interval for company generation (e.g., 10)
  driver_interval_seconds: number;       // Batch interval for driver events (e.g., 10)
  companies_per_batch: number;           // Number of companies per batch (e.g., 10)
  events_per_batch_range: [number, number]; // Min/max event count per batch (e.g., [5, 20])
}
```

**Field Constraints**:
- `company_interval_seconds`: Positive integer, typically 5-30 seconds
- `driver_interval_seconds`: Positive integer, typically 5-30 seconds
- `companies_per_batch`: Positive integer, typically 5-20 companies
- `events_per_batch_range`: Tuple of two positive integers where min ≤ max

**Validation**: Zod schema with optional() wrapper (may be absent in production mode)

**Nullability**: Entire object is optional - only present when generation_mode="emulated"

**Usage**: Displayed in EmulatedConfig component (Accordion), used for troubleshooting batch timing

---

### HealthData (Extended Interface)

Extended version of existing HealthData interface from feature 002 (spa-control).

**TypeScript Definition**:
```typescript
export interface HealthData {
  // Existing fields (from feature 002)
  status: string; // "running" | "paused"
  timestamp: string; // ISO 8601 timestamp
  uptime: {
    seconds: number;
    hours: number;
    start_time: string; // ISO 8601
  };
  company_generator: {
    total_batches: number;
    last_batch_time?: string; // ISO 8601, optional
    idle_seconds?: number | null;
  };
  driver_generator: {
    total_batches: number;
    last_batch_time?: string; // ISO 8601, optional
    last_interval_end?: string; // ISO 8601, optional
    idle_seconds?: number | null;
  };
  lifecycle: {
    paused: boolean;
    shutdown_requested: boolean;
  };
  
  // NEW FIELDS (feature 007)
  generation_mode?: GenerationMode;      // Optional for backward compatibility
  emulated_config?: EmulatedConfig;      // Optional, present only when mode="emulated"
}
```

**New Field Behaviors**:
- `generation_mode`: Defaults to "production" if missing (older backend)
- `emulated_config`: Only rendered when generation_mode="emulated" AND object present

**Migration Impact**: Existing components continue to work (new fields optional)

---

### BatchCadenceMetric (Derived)

Calculated metric for displaying batch generation rate.

**TypeScript Definition**:
```typescript
export interface BatchCadenceMetric {
  companyBatchesPerMinute: number | null;  // Null if uptime < 60 seconds
  driverBatchesPerMinute: number | null;   // Null if uptime < 60 seconds
}
```

**Calculation**:
```typescript
function calculateCadence(healthData: HealthData): BatchCadenceMetric {
  if (healthData.uptime.seconds < 60) {
    return { companyBatchesPerMinute: null, driverBatchesPerMinute: null };
  }
  
  const uptimeMinutes = healthData.uptime.seconds / 60;
  
  return {
    companyBatchesPerMinute: healthData.company_generator.total_batches / uptimeMinutes,
    driverBatchesPerMinute: healthData.driver_generator.total_batches / uptimeMinutes
  };
}
```

**Display Format**:
- Null: "—" or "Calculating..."
- Number: "6.2 batches/min" (1 decimal place, localized)

**Usage**: Displayed in BatchCadence component below generator statistics

---

## Component Props Interfaces

### ModeIndicatorProps

Props for mode indicator badge component.

```typescript
export interface ModeIndicatorProps {
  mode: GenerationMode;
  className?: string; // Optional for custom styling
}
```

---

### EmulatedConfigProps

Props for emulated configuration display component.

```typescript
export interface EmulatedConfigProps {
  config: EmulatedConfig;
  defaultExpanded?: boolean; // Accordion initial state, default false
}
```

---

### BatchCadenceProps

Props for batch cadence metric component.

```typescript
export interface BatchCadenceProps {
  metric: BatchCadenceMetric;
  mode: GenerationMode; // Affects display context (emulated vs production)
}
```

---

## State Management

**No Redux/Zustand Required**: All data flows from HealthPanel via existing polling mechanism.

**Component State**:
- ModeIndicator: Stateless (pure presentation)
- EmulatedConfig: Local state for accordion expand/collapse
- BatchCadence: Stateless (metric calculated from props)

**Polling**: Existing useInterval hook (5-second cycle) provides fresh data

**Error Handling**: Existing ErrorBoundary catches render failures

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────┐
│ /api/health (Backend - Feature 006)        │
│ {                                           │
│   generation_mode: "emulated",             │
│   emulated_config: {                       │
│     company_interval_seconds: 10,          │
│     driver_interval_seconds: 10,           │
│     companies_per_batch: 10,               │
│     events_per_batch_range: [5, 20]        │
│   },                                        │
│   company_generator: { total_batches: 24 },│
│   driver_generator: { total_batches: 24 }, │
│   uptime: { seconds: 240 }                 │
│ }                                           │
└─────────────────────────────────────────────┘
                    ↓ (5-second polling)
┌─────────────────────────────────────────────┐
│ HealthPanel.tsx                             │
│ - Fetches & validates with Zod             │
│ - Stores in local state: HealthData        │
└─────────────────────────────────────────────┘
         ↓                ↓                ↓
┌──────────────┐  ┌────────────────┐  ┌──────────────┐
│ ModeIndicator│  │ EmulatedConfig │  │ BatchCadence │
│ (mode prop)  │  │ (config prop)  │  │ (metric prop)│
└──────────────┘  └────────────────┘  └──────────────┘
```

---

## Validation Rules

### Zod Schemas (contracts/healthData.schema.ts)

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
  ]).refine(
    ([min, max]) => min <= max,
    { message: "events_per_batch_range min must be <= max" }
  )
}).optional();

export const HealthDataSchema = z.object({
  status: z.string(),
  timestamp: z.string(),
  uptime: z.object({
    seconds: z.number(),
    hours: z.number(),
    start_time: z.string()
  }),
  company_generator: z.object({
    total_batches: z.number(),
    last_batch_time: z.string().optional(),
    idle_seconds: z.number().nullable().optional()
  }),
  driver_generator: z.object({
    total_batches: z.number(),
    last_batch_time: z.string().optional(),
    last_interval_end: z.string().optional(),
    idle_seconds: z.number().nullable().optional()
  }),
  lifecycle: z.object({
    paused: z.boolean(),
    shutdown_requested: z.boolean()
  }),
  generation_mode: GenerationModeSchema,
  emulated_config: EmulatedConfigSchema
});

export type HealthData = z.infer<typeof HealthDataSchema>;
export type EmulatedConfig = z.infer<typeof EmulatedConfigSchema>;
export type GenerationMode = z.infer<typeof GenerationModeSchema>;
```

---

## Migration Notes

**Backward Compatibility**:
- Existing HealthPanel continues to work if backend lacks new fields
- New components conditionally render based on field presence
- No breaking changes to existing components (ThemeToggle, LogsPanel, etc.)

**Testing Strategy**:
- Unit tests: Mock HealthData with/without new fields
- Contract tests: Validate schema against live /api/health endpoint
- Integration tests: Verify graceful degradation when fields missing

**Rollout**: Safe to deploy frontend before backend update (degrades to production mode)

---

## Summary

**Total New Types**: 3 (GenerationMode enum, EmulatedConfig interface, BatchCadenceMetric interface)  
**Modified Types**: 1 (HealthData extended with 2 optional fields)  
**Validation**: Zod schemas with optional() and default() for backward compatibility  
**State Management**: Existing polling architecture, no global state changes  
**Persistence**: None (all data ephemeral, sourced from API every 5 seconds)
