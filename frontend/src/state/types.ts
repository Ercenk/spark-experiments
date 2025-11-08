// Shared TypeScript interfaces for Generator Control SPA

export interface Generator {
  id: string;
  status: 'running' | 'paused' | 'degraded';
  uptimeSeconds: number;
  lastActivityTs: string; // ISO 8601
  totalBatches: number;
  batchesPerMinute?: number;
  pausedAtTs?: string | null;
}

export interface HealthSnapshot {
  capturedTs: string;
  overallStatus: 'running' | 'paused' | 'degraded';
  generators: Generator[];
  totalBatches?: number;
  generationRatePerMin?: number;
}

export interface LifecycleStatus {
  status: 'running' | 'paused';
  paused: boolean;
  lastStateChangeTs: string;
}

export interface ControlResult {
  success: boolean;
  action: 'pause' | 'resume' | 'reset';
  status: 'running' | 'paused';
  timestamp: string;
  message?: string | null;
  error?: string | null;
}

export interface ResetResult extends ControlResult {
  filesRemoved?: number;
  durationMs?: number;
}

export interface LogEntry {
  ts: string;
  level: 'info' | 'warning' | 'error';
  message: string;
  source?: string;
  context?: Record<string, unknown> | null;
}

export interface LogsResponse {
  entries: LogEntry[];
  nextSince?: string | null;
  totalReturned?: number;
}

export interface AsyncActionState<T> {
  loading: boolean;
  error: string | null;
  data: T | null;
}

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'info';
  text: string;
}
