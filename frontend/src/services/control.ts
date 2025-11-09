import { apiClient } from './apiClient';
import { ControlResultSchema, ResetResultSchema } from './schemas';
import type { ControlResult, ResetResult } from './schemas';

export async function pause(): Promise<ControlResult> {
  const resp = await apiClient.post('/api/pause');
  return ControlResultSchema.parse(resp.data);
}

export async function resume(): Promise<ControlResult> {
  const resp = await apiClient.post('/api/resume');
  return ControlResultSchema.parse(resp.data);
}

export async function reset(): Promise<ResetResult> {
  const resp = await apiClient.post('/api/clean');
  const d = resp.data;
  if (d && typeof d === 'object' && d.deleted_count !== undefined) {
    return {
      success: d.success === undefined ? true : !!d.success,
      deleted_count: d.deleted_count || 0,
      deleted_items: Array.isArray(d.deleted_items) ? d.deleted_items : [],
      timestamp: d.timestamp || new Date().toISOString(),
      message: d.message || 'Data cleaned',
      errors: Array.isArray(d.errors) ? d.errors : undefined,
    } as ResetResult;
  }
  return ResetResultSchema.parse(d);
}
