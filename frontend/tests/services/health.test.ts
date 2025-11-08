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

  it('parses health snapshot', async () => {
    // Adjusted to match HealthSnapshotSchema expectations minimal shape
    mock.onGet('/health').reply(200, {
      capturedTs: '2025-11-08T00:00:00Z',
      overallStatus: 'running',
      generators: [],
      totalBatches: 0,
      generationRatePerMin: 0
    });
    const snapshot = await fetchHealth();
    expect(snapshot.overallStatus).toBe('running');
  });

  it('handles error response', async () => {
    mock.onGet('/health').reply(500, { error: 'fail' });
    await expect(fetchHealth()).rejects.toThrow();
  });
});
