import React from 'react';
import {
  Accordion,
  AccordionHeader,
  AccordionItem,
  AccordionPanel,
} from '@fluentui/react-components';
import type { EmulatedConfig as EmulatedConfigType } from '../services/schemas';

interface EmulatedConfigProps {
  config: EmulatedConfigType;
  defaultExpanded?: boolean;
}

/**
 * Display emulated mode configuration parameters
 * Feature 007: Emulated mode display (User Story 2)
 * 
 * Shows 4 key emulated mode configuration parameters in expandable accordion:
 * - Company interval (seconds)
 * - Driver interval (seconds)
 * - Companies per batch
 * - Events per batch range (min-max)
 * 
 * Collapsed by default to keep UI compact - users expand when troubleshooting.
 */
export const EmulatedConfig = React.memo<EmulatedConfigProps>(({ 
  config, 
  defaultExpanded = false 
}) => {
  if (!config) return null;
  
  return (
    <Accordion collapsible defaultOpenItems={defaultExpanded ? ['config'] : []}>
      <AccordionItem value="config">
        <AccordionHeader>Emulated Mode Configuration</AccordionHeader>
        <AccordionPanel>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: '1fr 1fr', 
            gap: '12px',
            padding: '8px 0'
          }}>
            <div>
              <strong>Company Interval:</strong> {config.company_interval_seconds}s
            </div>
            <div>
              <strong>Driver Interval:</strong> {config.driver_interval_seconds}s
            </div>
            <div>
              <strong>Companies/Batch:</strong> {config.companies_per_batch}
            </div>
            <div>
              <strong>Events/Batch:</strong> {config.events_per_batch_range[0]}-
              {config.events_per_batch_range[1]}
            </div>
          </div>
        </AccordionPanel>
      </AccordionItem>
    </Accordion>
  );
});
