import { apiClient } from './apiClient';
import { ControlResultSchema, ResetResultSchema } from './schemas';
import type { ControlResult, ResetResult } from './schemas';

export async function pause(): Promise<ControlResult> {
  const resp = await apiClient.post('/pause');
  return ControlResultSchema.parse(resp.data);
}

export async function resume(): Promise<ControlResult> {
  const resp = await apiClient.post('/resume');
  return ControlResultSchema.parse(resp.data);
}

export async function reset(): Promise<ResetResult> {
  const resp = await apiClient.post('/clean');
  return ResetResultSchema.parse(resp.data);
}
