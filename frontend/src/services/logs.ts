import { apiClient } from './apiClient';
import { LogsResponseSchema } from './schemas';
import type { LogsResponse } from './schemas';

export interface FetchLogsParams {
  limit?: number;
  since?: string;
  level?: 'info' | 'warning' | 'error';
}

export async function fetchLogs(params: FetchLogsParams = {}): Promise<LogsResponse> {
  const resp = await apiClient.get('/logs', { params });
  return LogsResponseSchema.parse(resp.data);
}
