import { apiClient } from './apiClient';
import { LogsResponseSchema } from './schemas';
import type { LogsResponse } from './schemas';
import { toApiError } from './apiErrors';

export interface FetchLogsParams {
  limit?: number;
  since?: string;
  level?: 'info' | 'warning' | 'error';
}

export async function fetchLogs(params: FetchLogsParams = {}, retry = 0): Promise<LogsResponse> {
  try {
    const resp = await apiClient.get('/api/logs', { params });
    return LogsResponseSchema.parse(resp.data);
  } catch (e: any) {
    const status = e?.response?.status;
    const transient = !status || (status >= 500 && status < 600);
    if (transient && retry < 2) {
      await new Promise(r => setTimeout(r, (retry + 1) * 300));
      return fetchLogs(params, retry + 1);
    }
    throw toApiError(e, '/api/logs');
  }
}
