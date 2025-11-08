import { z } from 'zod';

export const GeneratorSchema = z.object({
  id: z.string(),
  status: z.enum(['running', 'paused', 'degraded']),
  uptimeSeconds: z.number().nonnegative(),
  lastActivityTs: z.string(),
  totalBatches: z.number().nonnegative(),
  batchesPerMinute: z.number().nonnegative().optional(),
  pausedAtTs: z.string().nullable().optional(),
});

export const HealthSnapshotSchema = z.object({
  capturedTs: z.string(),
  overallStatus: z.enum(['running', 'paused', 'degraded']),
  generators: z.array(GeneratorSchema),
  totalBatches: z.number().optional(),
  generationRatePerMin: z.number().optional(),
});

export const LifecycleStatusSchema = z.object({
  status: z.enum(['running', 'paused']),
  paused: z.boolean(),
  lastStateChangeTs: z.string(),
});

export const ControlResultSchema = z.object({
  success: z.boolean(),
  action: z.enum(['pause', 'resume', 'reset']),
  status: z.enum(['running', 'paused']),
  timestamp: z.string(),
  message: z.string().nullable().optional(),
  error: z.string().nullable().optional(),
});

export const ResetResultSchema = ControlResultSchema.extend({
  filesRemoved: z.number().nonnegative().optional(),
  durationMs: z.number().nonnegative().optional(),
});

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

export type HealthSnapshot = z.infer<typeof HealthSnapshotSchema>;
export type LifecycleStatus = z.infer<typeof LifecycleStatusSchema>;
export type ControlResult = z.infer<typeof ControlResultSchema>;
export type ResetResult = z.infer<typeof ResetResultSchema>;
export type LogEntry = z.infer<typeof LogEntrySchema>;
export type LogsResponse = z.infer<typeof LogsResponseSchema>;
