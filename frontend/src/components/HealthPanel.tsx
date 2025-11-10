import React, { useEffect, useState, useCallback } from 'react';
import { fetchHealth, fetchStatus } from '../services/health';
import { useInterval } from '../hooks/useInterval';
import { Spinner, Button, Card, CardHeader, Badge } from '@fluentui/react-components';
import { pause, resume, reset } from '../services/control';
import { useToast } from './ToastProvider';
import { ModeIndicator } from './ModeIndicator';
import { EmulatedConfig } from './EmulatedConfig';
import { BatchCadence } from './BatchCadence';
import type { GenerationMode, EmulatedConfig as EmulatedConfigType } from '../services/schemas';

interface HealthData {
  status: string;
  timestamp: string;
  uptime: { seconds: number; hours: number; start_time: string };
  company_generator: { total_batches: number; last_batch_time?: string; idle_seconds?: number | null };
  driver_generator: { total_batches: number; last_batch_time?: string; last_interval_end?: string; idle_seconds?: number | null };
  lifecycle: { paused: boolean; shutdown_requested: boolean };
  // Feature 007: Emulated mode fields
  generation_mode?: GenerationMode;
  emulated_config?: EmulatedConfigType;
}

export const HealthPanel: React.FC = () => {
  const [data, setData] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { showError, showSuccess, showInfo } = useToast();

  const load = useCallback(async () => {
    try {
      const h = await fetchHealth();
      setData(h as unknown as HealthData); // casting to match simplified interface
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);
  useInterval(() => { load(); }, 5000);

  const doPause = async () => {
    try {
      const r = await pause();
      showSuccess(r.message || 'Paused');
      // Optimistic refresh
      load();
    } catch (e) {
      showError((e as Error).message);
    }
  };

  const doResume = async () => {
    try {
      const r = await resume();
      showSuccess(r.message || 'Resumed');
      load();
      // Poll for generation restart (batches increasing or auto reinit performed)
      const start = Date.now();
      const initial = data; // may be stale but used for comparison
      const poll = async () => {
        try {
          const h: any = await fetchHealth();
          const cg = h.company_generator?.total_batches ?? 0;
          const dg = h.driver_generator?.total_batches ?? 0;
          const cg0 = initial?.company_generator.total_batches ?? cg;
          const dg0 = initial?.driver_generator.total_batches ?? dg;
          const autoPerformed = h.auto_reinit?.performed;
          if (autoPerformed || cg > cg0 || dg > dg0) {
            showSuccess('Generation activity detected');
            return;
          }
          if (Date.now() - start < 20000) {
            setTimeout(poll, 1500);
          } else {
            showInfo('No new batches yet after resume');
          }
        } catch {
          if (Date.now() - start < 20000) setTimeout(poll, 2000);
        }
      };
      setTimeout(poll, 1500);
    } catch (e) {
      showError((e as Error).message);
    }
  };

  const doReset = async () => {
    if (!data?.lifecycle.paused) {
      showError('Pause first before reset');
      return;
    }
    try {
      const r = await reset();
      const deleted = (r as any).deleted_count ?? (r as any).filesRemoved;
      const errors = (r as any).errors as undefined | Array<any>;
      // Debug log for diagnosis
      // eslint-disable-next-line no-console
      console.debug('[reset] raw result', r);
      const treatAsSuccess = (deleted !== undefined && deleted >= 0) && (r.success === true || r.success === undefined || r.success === null);
      if (treatAsSuccess) {
        showSuccess((r.message || 'Reset complete') + (deleted !== undefined ? ` (removed ${deleted})` : ''));
      } else if (deleted !== undefined && deleted > 0) {
        const errCount = errors?.length || 0;
        showInfo(`Reset partial: removed ${deleted}${errCount ? `, ${errCount} errors` : ''}. ${r.message || ''}`.trim());
      } else if (r.success === false) {
        showError(r.message || 'Reset reported failure');
      } else {
        showError('Unexpected reset response');
      }
      load();
    } catch (e) {
      showError((e as Error).message);
    }
  };

  if (loading && !data) {
    return <Spinner label="Loading health..." />;
  }
  if (error && !data) {
    return <div role="alert">Error loading health: {error}</div>;
  }
  if (!data) return null;

  const statusColor = data.lifecycle.paused ? 'paused' : 'running';

  return (
    <Card style={{ marginTop: '1rem' }}>
      <CardHeader
        header={<span>Health & Status</span>}
        description={<span>Updates every 5s</span>}
        action={data.generation_mode ? <ModeIndicator mode={data.generation_mode} /> : undefined}
      />
      {data.generation_mode === 'emulated' && data.emulated_config && (
        <div style={{ marginBottom: '1rem' }}>
          <EmulatedConfig config={data.emulated_config} />
        </div>
      )}
      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
        <div>
          <strong>Overall Status: </strong>
          <Badge appearance={data.lifecycle.paused ? 'filled' : 'tint'}>{statusColor}</Badge>
        </div>
        <div><strong>Uptime:</strong> {data.uptime.hours}h ({data.uptime.seconds}s)</div>
        <div><strong>Last Company Batch:</strong> {data.company_generator.total_batches} ({data.company_generator.last_batch_time || 'n/a'})</div>
        <div><strong>Company Idle (s):</strong> {data.company_generator.idle_seconds ?? 'n/a'}</div>
        <div><strong>Last Driver Batch:</strong> {data.driver_generator.total_batches} ({data.driver_generator.last_batch_time || 'n/a'})</div>
        <div><strong>Driver Idle (s):</strong> {data.driver_generator.idle_seconds ?? 'n/a'}</div>
      </div>
      <BatchCadence 
        healthData={{
          uptime: data.uptime,
          company_generator: data.company_generator,
          driver_generator: data.driver_generator
        }}
        mode={data.generation_mode}
      />
      <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem' }}>
        {data.lifecycle.paused ? (
          <Button appearance="primary" onClick={doResume}>Resume</Button>
        ) : (
          <Button appearance="primary" onClick={doPause}>Pause</Button>
        )}
        <Button appearance="secondary" onClick={doReset} disabled={!data.lifecycle.paused}>Reset Data</Button>
        <Button appearance="secondary" onClick={load}>Refresh</Button>
      </div>
      {error && <div style={{ marginTop: '0.5rem', color: '#d13438' }}>Last error: {error}</div>}
    </Card>
  );
};
