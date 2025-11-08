import React, { useEffect, useState, useCallback } from 'react';
import { fetchLogs } from '../services/logs';
import { Button, Spinner, Dropdown, Option, Switch } from '@fluentui/react-components';

interface LogEntryUI {
  ts: string;
  level: string;
  message: string;
  source?: string;
}

export const LogsPanel: React.FC = () => {
  const [entries, setEntries] = useState<LogEntryUI[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [level, setLevel] = useState<string | undefined>(undefined);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [nextSince, setNextSince] = useState<string | undefined>(undefined);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const resp = await fetchLogs({ limit: 50, level: level as any });
      setEntries(resp.entries as LogEntryUI[]);
      setNextSince(resp.nextSince || undefined);
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }, [level]);

  const loadMore = useCallback(async () => {
    if (!nextSince || loading) return;
    setLoading(true);
    try {
      const resp = await fetchLogs({ limit: 50, level: level as any, since: nextSince });
      // merge without duplicates
      const existingKeys = new Set(entries.map(e => e.ts + e.message));
      const newEntries = resp.entries.filter(e => !existingKeys.has(e.ts + e.message)) as LogEntryUI[];
      setEntries([...entries, ...newEntries]);
      setNextSince(resp.nextSince || undefined);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }, [nextSince, loading, level, entries]);

  useEffect(() => { load(); }, [load]);
  useEffect(() => {
    if (!autoRefresh) return;
    const id = setInterval(() => { load(); }, 8000);
    return () => clearInterval(id);
  }, [autoRefresh, load]);

  return (
    <div style={{ marginTop: '1rem' }}>
      <h2 style={{ marginBottom: '0.5rem' }}>Recent Logs (stub)</h2>
      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <Button onClick={load} disabled={loading}>Refresh</Button>
        <Switch checked={autoRefresh} onChange={(e) => setAutoRefresh(e.target.checked)}>Auto-refresh</Switch>
        <Dropdown placeholder="Level" selectedOptions={level ? [level] : []} onOptionSelect={(_, data) => setLevel(data.optionValue === 'all' ? undefined : data.optionValue)}>
          <Option value="all">All</Option>
          <Option value="info">Info</Option>
          <Option value="warning">Warning</Option>
          <Option value="error">Error</Option>
        </Dropdown>
        <Button onClick={loadMore} disabled={loading || !nextSince}>Load More</Button>
      </div>
      {loading && <Spinner label="Loading logs" />}
      {error && <div style={{ color: '#d13438' }}>Error: {error}</div>}
      <div style={{ maxHeight: 320, overflowY: 'auto', marginTop: '0.5rem', fontFamily: 'monospace', fontSize: 12, border: '1px solid #ddd', padding: '4px' }}>
        {entries.map((e) => (
          <div key={e.ts + e.message}>
            <strong>[{e.level}]</strong> {e.ts} {e.source ? '(' + e.source + ') ' : ''}- {e.message}
          </div>
        ))}
        {entries.length === 0 && !loading && <div>No log entries.</div>}
      </div>
    </div>
  );
};
