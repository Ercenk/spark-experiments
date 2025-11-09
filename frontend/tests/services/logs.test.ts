import { describe, it, expect, beforeEach } from 'vitest';
import MockAdapter from 'axios-mock-adapter';
import { apiClient } from '../../src/services/apiClient';
import { fetchLogs } from '../../src/services/logs';

describe('logs service', () => {
  let mock: MockAdapter;
  beforeEach(() => {
    mock = new MockAdapter(apiClient);
    mock.reset();
  });

  it('returns parsed entries', async () => {
    mock.onGet('/api/logs').reply(200, {
      entries: [
        { ts: '2025-11-08T00:00:00Z', level: 'info', message: 'hello', source: 'orchestrator' }
      ],
      totalReturned: 1
    });
    const resp = await fetchLogs({ limit: 5 });
    expect(resp.entries.length).toBe(1);
    expect(resp.entries[0].message).toBe('hello');
  });

  it('handles server error', async () => {
    mock.onGet('/api/logs').reply(500, { error: 'boom' });
    await expect(fetchLogs({ limit: 5 })).rejects.toThrow();
  });
});
