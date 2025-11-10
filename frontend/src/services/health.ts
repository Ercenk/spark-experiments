import { apiClient } from './apiClient';
import { HealthResponseSchema, LifecycleStatusSchema, BlueprintHealthSnapshotSchema } from './schemas';
import type { HealthResponse, LifecycleStatus } from './schemas';

// Transform blueprint snapshot shape into legacy HealthResponse shape expected by UI components.
function adaptBlueprintSnapshot(raw: any): HealthResponse {
  const snap = BlueprintHealthSnapshotSchema.parse(raw);
  const uptimeSeconds = snap.uptime_seconds;
  const uptime = {
    seconds: uptimeSeconds,
    hours: Number((uptimeSeconds / 3600).toFixed(2)),
    start_time: snap.start_time,
  };
  const now = new Date(snap.timestamp).getTime();
  const idleCompany = snap.last_company_time ? Math.max(0, (now - new Date(snap.last_company_time).getTime()) / 1000) : null;
  const idleDriver = snap.last_driver_time ? Math.max(0, (now - new Date(snap.last_driver_time).getTime()) / 1000) : null;

  const companyGen = {
    total_batches: snap.company_batches,
    last_batch_time: snap.last_company_time ?? null,
    idle_seconds: idleCompany === null ? null : Number(idleCompany.toFixed(1)),
  };
  const driverGen = {
    total_batches: snap.driver_batches,
    last_batch_time: snap.last_driver_time ?? null,
    idle_seconds: idleDriver === null ? null : Number(idleDriver.toFixed(1)),
    last_interval_end: null,
  };
  const lifecycle = {
    paused: snap.paused,
    shutdown_requested: snap.shutdown_requested,
  };
  const state = {
    last_saved: snap.timestamp, // blueprint snapshot does not expose saved_at; use timestamp
    state_file: 'data/manifests/generator_state.json',
  };
  const auto_reinit = {
    performed: false,
    at: null,
    actions: [],
    missing_files: [],
  };
  
  // Feature 007: Pass through emulated mode fields from backend
  const generation_mode = (raw as any).generation_mode;
  const emulated_config = (raw as any).emulated_config;
  
  return HealthResponseSchema.parse({
    status: snap.status,
    timestamp: snap.timestamp,
    uptime,
    company_generator: companyGen,
    driver_generator: driverGen,
    lifecycle,
    state,
    auto_reinit,
    generation_mode,
    emulated_config,
  });
}

export async function fetchHealth(): Promise<HealthResponse> {
  const resp = await apiClient.get('/api/health');
  // Always blueprint now; adapt shape.
  return adaptBlueprintSnapshot(resp.data);
}

export async function fetchStatus(): Promise<LifecycleStatus> {
  const health = await fetchHealth();
  return LifecycleStatusSchema.parse({
    status: health.status,
    paused: health.lifecycle.paused,
    lastStateChangeTs: health.timestamp,
  });
}
