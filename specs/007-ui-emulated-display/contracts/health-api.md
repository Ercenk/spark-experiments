# API Contract: Enhanced Health Endpoint

**Feature**: 007-ui-emulated-display  
**Endpoint**: `GET /api/health`  
**Created**: 2025-11-09  
**Backend Feature**: 006-emulated-generation (already implemented)

## Overview

This contract documents the enhanced `/api/health` endpoint response schema for emulated mode display. **No new endpoint created** - this feature consumes existing API enhancements from feature 006.

## Request

```http
GET /api/health HTTP/1.1
Host: localhost:18000
Accept: application/json
```

**Query Parameters**: None  
**Headers**: None required  
**Authentication**: None (local development environment)

## Response (Production Mode)

**HTTP Status**: 200 OK  
**Content-Type**: application/json

```json
{
  "status": "running",
  "timestamp": "2025-11-09T14:30:00.000Z",
  "uptime": {
    "seconds": 3600.5,
    "hours": 1.0,
    "start_time": "2025-11-09T13:30:00.000Z"
  },
  "company_generator": {
    "total_batches": 1,
    "last_batch_time": "2025-11-09T14:00:00.000Z",
    "idle_seconds": 1800.0
  },
  "driver_generator": {
    "total_batches": 4,
    "last_batch_time": "2025-11-09T14:15:00.000Z",
    "last_interval_end": "2025-11-09T14:15:00.000Z",
    "idle_seconds": 900.0
  },
  "lifecycle": {
    "paused": false,
    "shutdown_requested": false
  },
  "generation_mode": "production",
  "emulated_config": null
}
```

**Field Notes**:
- `generation_mode`: Always "production" when backend running in standard mode
- `emulated_config`: Null (not present) in production mode

## Response (Emulated Mode)

**HTTP Status**: 200 OK  
**Content-Type**: application/json

```json
{
  "status": "running",
  "timestamp": "2025-11-09T14:32:00.000Z",
  "uptime": {
    "seconds": 240.0,
    "hours": 0.067,
    "start_time": "2025-11-09T14:28:00.000Z"
  },
  "company_generator": {
    "total_batches": 24,
    "last_batch_time": "2025-11-09T14:31:50.000Z",
    "idle_seconds": 10.0
  },
  "driver_generator": {
    "total_batches": 24,
    "last_batch_time": "2025-11-09T14:31:50.000Z",
    "last_interval_end": "2025-11-09T14:32:00.000Z",
    "idle_seconds": 10.0
  },
  "lifecycle": {
    "paused": false,
    "shutdown_requested": false
  },
  "generation_mode": "emulated",
  "emulated_config": {
    "company_interval_seconds": 10,
    "driver_interval_seconds": 10,
    "companies_per_batch": 10,
    "events_per_batch_range": [5, 20]
  }
}
```

**Field Notes**:
- `generation_mode`: "emulated" when backend running with emulated config
- `emulated_config`: Object with 4 configuration parameters
- `total_batches`: Much higher than production (24 batches in 4 minutes vs 1 batch per hour)

## Response (Legacy Backend - No Mode Fields)

**HTTP Status**: 200 OK  
**Content-Type**: application/json

```json
{
  "status": "running",
  "timestamp": "2025-11-09T14:30:00.000Z",
  "uptime": {
    "seconds": 3600.5,
    "hours": 1.0,
    "start_time": "2025-11-09T13:30:00.000Z"
  },
  "company_generator": {
    "total_batches": 1,
    "last_batch_time": "2025-11-09T14:00:00.000Z",
    "idle_seconds": 1800.0
  },
  "driver_generator": {
    "total_batches": 4,
    "last_batch_time": "2025-11-09T14:15:00.000Z",
    "last_interval_end": "2025-11-09T14:15:00.000Z",
    "idle_seconds": 900.0
  },
  "lifecycle": {
    "paused": false,
    "shutdown_requested": false
  }
}
```

**Field Notes**:
- `generation_mode`: Missing (older backend without feature 006)
- Frontend behavior: Defaults to "production" mode, hides mode indicator

## Error Responses

### Service Unavailable

**HTTP Status**: 503 Service Unavailable

```json
{
  "error": "Generator not running",
  "message": "Health check failed - service unavailable"
}
```

**Frontend Handling**: Display error state in HealthPanel, retry after 5 seconds

### Invalid Response (Malformed JSON)

**Frontend Handling**: Zod schema validation fails, caught by ErrorBoundary, toast notification shown

## Zod Schema (TypeScript)

```typescript
import { z } from 'zod';

const GenerationModeSchema = z.enum(['production', 'emulated'])
  .default('production');

const EmulatedConfigSchema = z.object({
  company_interval_seconds: z.number().positive(),
  driver_interval_seconds: z.number().positive(),
  companies_per_batch: z.number().positive().int(),
  events_per_batch_range: z.tuple([
    z.number().positive().int(),
    z.number().positive().int()
  ])
}).optional().nullable();

const UptimeSchema = z.object({
  seconds: z.number(),
  hours: z.number(),
  start_time: z.string()
});

const GeneratorStatsSchema = z.object({
  total_batches: z.number(),
  last_batch_time: z.string().optional(),
  idle_seconds: z.number().nullable().optional()
});

const DriverGeneratorStatsSchema = GeneratorStatsSchema.extend({
  last_interval_end: z.string().optional()
});

const LifecycleSchema = z.object({
  paused: z.boolean(),
  shutdown_requested: z.boolean()
});

export const HealthDataSchema = z.object({
  status: z.string(),
  timestamp: z.string(),
  uptime: UptimeSchema,
  company_generator: GeneratorStatsSchema,
  driver_generator: DriverGeneratorStatsSchema,
  lifecycle: LifecycleSchema,
  generation_mode: GenerationModeSchema,
  emulated_config: EmulatedConfigSchema
});

export type HealthData = z.infer<typeof HealthDataSchema>;
```

## Polling Behavior

**Interval**: 5 seconds (existing pattern from feature 002)  
**Method**: HTTP GET via Axios  
**Timeout**: 10 seconds (default Axios timeout)  
**Retry Logic**: None (next poll in 5 seconds handles transient failures)

## Contract Testing

**Test File**: `frontend/tests/contract/healthContract.test.ts`

**Test Cases**:
1. ✅ Production mode response validates against schema
2. ✅ Emulated mode response validates against schema
3. ✅ Legacy response (missing mode fields) validates with defaults
4. ✅ Invalid schema (wrong types) throws Zod error
5. ✅ Service unavailable (503) handled gracefully

**Example Test**:
```typescript
import { describe, test, expect } from 'vitest';
import { HealthDataSchema } from '../src/services/schemas';
import { fetchHealth } from '../src/services/health';

describe('Health API Contract', () => {
  test('emulated mode response validates', async () => {
    const data = await fetchHealth();
    const result = HealthDataSchema.safeParse(data);
    expect(result.success).toBe(true);
    
    if (result.success && result.data.generation_mode === 'emulated') {
      expect(result.data.emulated_config).toBeDefined();
      expect(result.data.emulated_config?.company_interval_seconds).toBeGreaterThan(0);
    }
  });
  
  test('legacy response defaults to production mode', () => {
    const legacyData = {
      status: 'running',
      timestamp: '2025-11-09T14:30:00.000Z',
      uptime: { seconds: 100, hours: 0.028, start_time: '2025-11-09T14:28:00.000Z' },
      company_generator: { total_batches: 1 },
      driver_generator: { total_batches: 1 },
      lifecycle: { paused: false, shutdown_requested: false }
    };
    
    const result = HealthDataSchema.parse(legacyData);
    expect(result.generation_mode).toBe('production');
  });
});
```

## Backward Compatibility Guarantees

1. **Additive Only**: New fields (`generation_mode`, `emulated_config`) are additive - existing clients ignore them
2. **Optional Fields**: Both new fields have safe defaults (production mode, null config)
3. **No Breaking Changes**: Existing HealthPanel continues to work with old or new backend
4. **Graceful Degradation**: Frontend hides mode indicator if fields missing

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-09 | Initial contract for feature 007 (consumes feature 006 backend) |

## References

- Backend API Implementation: `specs/006-emulated-generation/contracts/api-enhancements.md`
- Frontend Health Service: `frontend/src/services/health.ts`
- Zod Schemas: `frontend/src/services/schemas.ts`
