import { z } from 'zod';

// Backend-aligned health response schemas
export const UptimeSchema = z.object({
  seconds: z.number(),
  hours: z.number(),
  start_time: z.string(),
});

export const GeneratorStatsSchema = z.object({
  total_batches: z.number().nonnegative(),
  last_batch_time: z.string().nullable().optional(),
  idle_seconds: z.number().nullable().optional(),
  last_interval_end: z.string().nullable().optional(),
});

export const LifecycleSchema = z.object({
  paused: z.boolean(),
  shutdown_requested: z.boolean(),
});

export const StateSchema = z.object({
  last_saved: z.string().nullable().optional(),
  state_file: z.string(),
});

export const AutoReinitSchema = z.object({
  performed: z.boolean(),
  at: z.string().nullable().optional(),
  actions: z.array(z.string()),
  missing_files: z.array(z.string()),
});

export const HealthResponseSchema = z.object({
  status: z.enum(['running', 'paused']),
  timestamp: z.string(),
  uptime: UptimeSchema,
  company_generator: GeneratorStatsSchema,
  driver_generator: GeneratorStatsSchema,
  lifecycle: LifecycleSchema,
  state: StateSchema,
  auto_reinit: AutoReinitSchema,
});

// Blueprint snapshot raw shape (from /api/health) prior to adaptation
export const BlueprintHealthSnapshotSchema = z.object({
  status: z.enum(['running', 'paused']),
  timestamp: z.string(),
  uptime_seconds: z.number(),
  start_time: z.string(),
  company_batches: z.number().nonnegative(),
  driver_batches: z.number().nonnegative(),
  last_company_time: z.string().nullable().optional(),
  last_driver_time: z.string().nullable().optional(),
  paused: z.boolean(),
  shutdown_requested: z.boolean(),
  verification: z.any().optional(),
});

// Derived simplified lifecycle status for UI convenience
export const LifecycleStatusSchema = z.object({
  status: z.enum(['running', 'paused']),
  paused: z.boolean(),
  lastStateChangeTs: z.string(),
});

export const ControlResultSchema = z.object({
  success: z.boolean(),
  action: z.enum(['pause', 'resume']).optional(), // decoupled control excludes reset; clean returns separate shape
  status: z.enum(['running', 'paused']).optional(),
  timestamp: z.string().optional(),
  message: z.string().nullable().optional(),
  error: z.string().nullable().optional(),
  extra: z.record(z.any()).nullable().optional(), // baseline verification payload after resume
});

// Clean endpoint specific schema (backend returns deleted_count/deleted_items)
export const CleanResultSchema = z.object({
  success: z.boolean(),
  deleted_count: z.number().nonnegative(),
  deleted_items: z.array(z.object({
    name: z.string(),
    path: z.string(),
    type: z.string(),
    size: z.number().nonnegative().optional(),
    file_count: z.number().nonnegative().optional()
  })),
  timestamp: z.string(),
  message: z.string().nullable().optional(),
  errors: z.array(z.object({
    name: z.string(),
    path: z.string(),
    error: z.string()
  })).optional()
});

export const ResetResultSchema = CleanResultSchema; // alias for existing usage

export const LogEntrySchema = z.object({
  ts: z.string(),
  level: z.enum(['info', 'warning', 'error']),
  message: z.string(),
  source: z.string().optional(),
  context: z.record(z.any()).nullable().optional(),
});

export const LogsResponseSchema = z.object({
  entries: z.array(LogEntrySchema),
  nextSince: z.string().nullable().optional(),
  totalReturned: z.number().optional(),
});
export type HealthResponse = z.infer<typeof HealthResponseSchema>;
export type LifecycleStatus = z.infer<typeof LifecycleStatusSchema>;
export type ControlResult = z.infer<typeof ControlResultSchema>;
export type ResetResult = z.infer<typeof ResetResultSchema>;
export type LogEntry = z.infer<typeof LogEntrySchema>;
export type LogsResponse = z.infer<typeof LogsResponseSchema>;
export type BlueprintHealthSnapshot = z.infer<typeof BlueprintHealthSnapshotSchema>;
