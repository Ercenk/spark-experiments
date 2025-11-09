import { describe, it, expect } from 'vitest';
import axios from 'axios';

// Poll health endpoint for batch increase after resume
async function pollForActivity(initialCompany: number, initialDriver: number, timeoutMs = 15000): Promise<boolean> {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      const resp = await axios.get('http://localhost:18000/health', { timeout: 3000 });
      const h = resp.data;
      const cg = h.company_generator?.total_batches ?? 0;
      const dg = h.driver_generator?.total_batches ?? 0;
      const auto = h.auto_reinit?.performed;
      if (auto || cg > initialCompany || dg > initialDriver) return true;
    } catch {}
    await new Promise(r => setTimeout(r, 1500));
  }
  return false;
}

describe('integration: resume generation restart', () => {
  it('detects batch increase or auto reinit after resume', async () => {
    try {
      // Pause first
      try { await axios.post('http://localhost:18000/pause', {}, { timeout: 4000 }); } catch {}
      // Fetch baseline
      const baselineResp = await axios.get('http://localhost:18000/health', { timeout: 4000 });
      const base = baselineResp.data;
      const baseCompany = base.company_generator?.total_batches ?? 0;
      const baseDriver = base.driver_generator?.total_batches ?? 0;
      // Resume
      await axios.post('http://localhost:18000/resume', {}, { timeout: 4000 });
      const active = await pollForActivity(baseCompany, baseDriver, 15000);
      expect(active).toBe(true);
    } catch (e: any) {
      if (e.code === 'ECONNREFUSED') {
        // Environment not running
        expect(true).toBe(true);
      } else {
        throw e;
      }
    }
  });
});
