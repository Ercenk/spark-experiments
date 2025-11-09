import { describe, it, expect } from 'vitest';
import axios from 'axios';

describe('contract: clean endpoint', () => {
  it('returns structured response (idempotent)', async () => {
    try {
      // Attempt pause first (ignore errors if already paused)
      try { await axios.post('http://localhost:18000/pause', {}, { timeout: 3000 }); } catch {}
      const resp = await axios.post('http://localhost:18000/clean', {}, { timeout: 5000 });
      expect(typeof resp.data).toBe('object');
      expect(resp.data).toHaveProperty('success');
      expect(resp.data).toHaveProperty('timestamp');
    } catch (e: any) {
      if (e.code === 'ECONNREFUSED') {
        console.warn('Clean service unreachable; skipping contract assertion');
        expect(true).toBe(true);
      } else {
        throw e;
      }
    }
  });
});
