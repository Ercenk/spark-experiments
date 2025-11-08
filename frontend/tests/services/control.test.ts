import { describe, it, expect, beforeEach } from 'vitest';
import MockAdapter from 'axios-mock-adapter';
import { apiClient } from '../../src/services/apiClient';
import { pause, resume, reset } from '../../src/services/control';

describe('control services', () => {
  let mock: MockAdapter;
  beforeEach(() => {
    mock = new MockAdapter(apiClient);
    mock.reset();
  });

  it('pause success', async () => {
    mock.onPost('/pause').reply(200, { success: true, action: 'pause', status: 'paused', timestamp: '2025-11-08T00:00:00Z' });
    const r = await pause();
    expect(r.status).toBe('paused');
  });

  it('resume success', async () => {
    mock.onPost('/resume').reply(200, { success: true, action: 'resume', status: 'running', timestamp: '2025-11-08T00:00:00Z' });
    const r = await resume();
    expect(r.status).toBe('running');
  });

  it('reset requires paused', async () => {
    mock.onPost('/clean').reply(400, { error: 'must pause' });
    await expect(reset()).rejects.toThrow();
  });
});
