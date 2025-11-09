import { describe, it, expect } from 'vitest';
import axios from 'axios';
import { HealthResponseSchema } from '../../src/services/schemas';

// Basic contract test hitting live generator if available
describe('contract: health endpoint', () => {
  it('matches schema shape', async () => {
    try {
      const resp = await axios.get('http://localhost:18000/api/health', { timeout: 3000 });
      const parsed = HealthResponseSchema.parse(resp.data);
      expect(parsed.status).toMatch(/running|paused/);
      expect(parsed.uptime.seconds).toBeGreaterThanOrEqual(0);
    } catch (e: any) {
      // Allow test to pass gracefully if service not running in CI
      if (e.code === 'ECONNREFUSED') {
        console.warn('Health service unreachable; skipping contract assertion');
        expect(true).toBe(true);
      } else {
        throw e;
      }
    }
  });
});
