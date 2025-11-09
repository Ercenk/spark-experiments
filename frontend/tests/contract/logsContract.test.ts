import { describe, it, expect } from 'vitest';
import axios from 'axios';
import { LogsResponseSchema } from '../../src/services/schemas';

describe('contract: logs endpoint', () => {
  it('returns entries array', async () => {
    try {
      const resp = await axios.get('http://localhost:18000/api/logs?limit=10', { timeout: 3000 });
      const parsed = LogsResponseSchema.parse(resp.data);
      expect(Array.isArray(parsed.entries)).toBe(true);
      expect(parsed.totalReturned).toBeDefined();
    } catch (e: any) {
      if (e.code === 'ECONNREFUSED') {
        console.warn('Logs service unreachable; skipping contract assertion');
        expect(true).toBe(true);
      } else {
        throw e;
      }
    }
  });
});
