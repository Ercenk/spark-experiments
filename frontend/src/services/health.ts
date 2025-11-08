import { apiClient } from './apiClient';
import { HealthSnapshotSchema, LifecycleStatusSchema } from './schemas';
import type { HealthSnapshot, LifecycleStatus } from './schemas';

export async function fetchHealth(): Promise<HealthSnapshot> {
  const resp = await apiClient.get('/health');
  return HealthSnapshotSchema.parse(resp.data);
}

export async function fetchStatus(): Promise<LifecycleStatus> {
  const resp = await apiClient.get('/status');
  return LifecycleStatusSchema.parse(resp.data);
}
