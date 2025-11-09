import { describe, it, expect, beforeEach } from 'vitest';
import MockAdapter from 'axios-mock-adapter';
import { apiClient } from '../../src/services/apiClient';
import { fetchHealth } from '../../src/services/health';

describe('health service', () => {
  let mock: MockAdapter;
  beforeEach(() => {
    mock = new MockAdapter(apiClient);
    mock.reset();
  });

  it('parses backend-aligned health response', async () => {
    mock.onGet('/api/health').reply(200, {
      status: 'running',
      timestamp: '2025-11-08T00:00:00Z',
      uptime: { seconds: 10.5, hours: 0.01, start_time: '2025-11-08T00:00:00Z' },
      company_generator: { total_batches: 3, last_batch_time: '2025-11-08T00:00:05Z', idle_seconds: 2.1 },
      driver_generator: { total_batches: 5, last_batch_time: '2025-11-08T00:00:06Z', last_interval_end: null, idle_seconds: 1.4 },
      lifecycle: { paused: false, shutdown_requested: false },
      state: { last_saved: '2025-11-08T00:00:07Z', state_file: 'data/manifests/generator_state.json' },
      auto_reinit: { performed: false, at: null, actions: [], missing_files: [] }
    });
    const snapshot = await fetchHealth();
    expect(snapshot.status).toBe('running');
    expect(snapshot.lifecycle.paused).toBe(false);
    expect(snapshot.company_generator.total_batches).toBe(3);
  });

  it('handles error response', async () => {
    mock.onGet('/api/health').reply(500, { error: 'fail' });
    await expect(fetchHealth()).rejects.toThrow();
  });
});
