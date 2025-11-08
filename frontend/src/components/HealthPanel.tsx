import React, { useEffect, useState, useCallback } from 'react';
import { fetchHealth, fetchStatus } from '../services/health';
import { useInterval } from '../hooks/useInterval';
import { Spinner, Button, Card, CardHeader, Badge } from '@fluentui/react-components';
import { pause, resume, reset } from '../services/control';
import { useToast } from './ToastProvider';

interface HealthData {
  status: string;
  timestamp: string;
  uptime: { seconds: number; hours: number; start_time: string };
  company_generator: { total_batches: number; last_batch_time?: string; idle_seconds?: number | null };
  driver_generator: { total_batches: number; last_batch_time?: string; last_interval_end?: string; idle_seconds?: number | null };
  lifecycle: { paused: boolean; shutdown_requested: boolean };
}

export const HealthPanel: React.FC = () => {
  const [data, setData] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { showError, showSuccess } = useToast();

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
      showSuccess(r.message || 'Reset complete');
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
      />
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
