# Data Model: Generator Control SPA

## Overview
Single-page application consumes operational data from existing generator backend. No persistence layer. All models are transient representations of API responses.

## Entities

### Generator
Represents a logical data generation process.
- id: string (e.g., "company", "driver-events")
- status: enum("running" | "paused" | "degraded") [initial release uses running|paused]
- uptimeSeconds: number (integer)
- lastActivityTs: ISO 8601 string
- totalBatches: number
- batchesPerMinute: number (derived client-side: delta batches / elapsed minutes)
- pausedAtTs: ISO 8601 string | null

### HealthSnapshot
Aggregated system health + per-generator metrics.
- capturedTs: ISO 8601 string
- overallStatus: enum("running" | "paused" | "degraded")
- generators: Generator[]
- totalBatches: number (sum of generators.totalBatches)
- generationRatePerMin: number (sum of generators.batchesPerMinute)

### LifecycleStatus
Concise representation for status polling.
- status: enum("running" | "paused")
- paused: boolean
- lastStateChangeTs: ISO 8601 string

### ControlResult
Uniform response for pause/resume/reset.
- success: boolean
- action: enum("pause" | "resume" | "reset")
- status: enum("running" | "paused") (post-action state)
- timestamp: ISO 8601 string
- message: string | null
- error: string | null

### ResetResult
Specialization of ControlResult for reset.
- (inherits ControlResult)
- filesRemoved: number
- durationMs: number

### LogEntry
Structured log item.
- ts: ISO 8601 string
- level: enum("info" | "warning" | "error")
- message: string
- source: string (generator id or system)
- context: object | null (additional structured properties)

### LogsResponse
Wrapper for log fetch.
- entries: LogEntry[]
- nextSince: ISO 8601 string | null (timestamp for incremental fetch)
- totalReturned: number

### ErrorState (client-side only)
Represents transient UI error conditions.
- scope: enum("health" | "control" | "logs")
- message: string
- occurredAt: ISO 8601 string
- retryCount: number

## State Transitions

### Generator Status
```
RUNNING --(pause)--> PAUSED
PAUSED --(resume)--> RUNNING
RUNNING --(failure detection future)--> DEGRADED
DEGRADED --(manual intervention future)--> RUNNING
```
Initial release implements only RUNNING <-> PAUSED.

### Reset Flow
```
[PAUSED] --(reset request)--> [PAUSED + data cleared] --(resume optional)--> [RUNNING fresh]
```
Reset is blocked if state is RUNNING.

## Validation Rules
- limit (logs): 1 <= limit <= 500
- since: must be valid ISO 8601; if provided, only entries with ts > since included
- Action responses must set success=false when HTTP status >=400
- LogEntry.message length <= 2000 chars (defensive UI truncation beyond)

## Derived Fields
- batchesPerMinute (client): calculate using previous snapshot difference / elapsed minutes
- generationRatePerMin (client): sum of per-generator rates

## Notes
- No pagination beyond `limit` for initial version
- `nextSince` enables future infinite scroll or incremental polling
- `degraded` reserved for future fault scenarios
