import React, { useMemo } from 'react';
import type { GenerationMode } from '../services/schemas';

interface HealthData {
  uptime: { seconds: number };
  company_generator: { total_batches: number };
  driver_generator: { total_batches: number };
}

interface BatchCadenceProps {
  healthData: HealthData;
  mode?: GenerationMode;
}

interface CadenceMetric {
  companyBatchesPerMinute: number | null;
  driverBatchesPerMinute: number | null;
}

/**
 * Calculate and display batch generation cadence (batches per minute)
 * Feature 007: Emulated mode display (User Story 3)
 * 
 * Calculates batches/minute for both company and driver generators.
 * Shows "Calculating..." for uptime < 60 seconds (insufficient data).
 * Particularly valuable in emulated mode to demonstrate fast cadence (6/min vs 0.01-4/min production).
 * 
 * Calculation: total_batches / (uptime_seconds / 60)
 */
export const BatchCadence = React.memo<BatchCadenceProps>(({ healthData, mode }) => {
  const cadence: CadenceMetric = useMemo(() => {
    if (healthData.uptime.seconds < 60) {
      return { companyBatchesPerMinute: null, driverBatchesPerMinute: null };
    }
    
    const uptimeMinutes = healthData.uptime.seconds / 60;
    
    return {
      companyBatchesPerMinute: healthData.company_generator.total_batches / uptimeMinutes,
      driverBatchesPerMinute: healthData.driver_generator.total_batches / uptimeMinutes,
    };
  }, [healthData.uptime.seconds, healthData.company_generator.total_batches, healthData.driver_generator.total_batches]);

  const formatCadence = (value: number | null): string => {
    if (value === null) return 'Calculating...';
    return `${value.toFixed(1)} batches/min`;
  };

  return (
    <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
      <div style={{ marginBottom: '4px', fontWeight: 600, fontSize: '14px' }}>
        Batch Cadence {mode === 'emulated' ? '(Emulated Mode)' : ''}
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
        <div>
          <strong>Company Batches:</strong> {formatCadence(cadence.companyBatchesPerMinute)}
        </div>
        <div>
          <strong>Driver Batches:</strong> {formatCadence(cadence.driverBatchesPerMinute)}
        </div>
      </div>
      {healthData.uptime.seconds < 60 && (
        <div style={{ marginTop: '8px', fontSize: '12px', color: '#666', fontStyle: 'italic' }}>
          Cadence metrics available after 60 seconds of uptime
        </div>
      )}
    </div>
  );
});
