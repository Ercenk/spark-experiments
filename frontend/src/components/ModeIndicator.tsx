import React from 'react';
import { Badge } from '@fluentui/react-components';
import { BeakerRegular, CheckmarkCircleRegular } from '@fluentui/react-icons';
import type { GenerationMode } from '../services/schemas';
import { useModeStyles } from '../styles/modeStyles';

interface ModeIndicatorProps {
  mode: GenerationMode;
  className?: string;
}

/**
 * Display generation mode indicator badge
 * Feature 007: Emulated mode display (User Story 1)
 * 
 * Shows prominent badge indicating current generator operation mode:
 * - Emulated: Orange badge with beaker icon + "Emulated Mode" text
 * - Production: Gray badge with checkmark icon + "Production Mode" text
 * 
 * WCAG 2.1 AA compliant: Color + icon + text for non-color visual cues
 */
export const ModeIndicator = React.memo<ModeIndicatorProps>(({ mode, className }) => {
  const styles = useModeStyles();
  
  if (mode === 'emulated') {
    return (
      <Badge
        color="warning"
        icon={<BeakerRegular />}
        appearance="filled"
        size="large"
        className={`${styles.emulatedBadge} ${className || ''}`}
      >
        Emulated Mode
      </Badge>
    );
  }
  
  return (
    <Badge
      color="subtle"
      icon={<CheckmarkCircleRegular />}
      appearance="outline"
      size="large"
      className={`${styles.productionBadge} ${className || ''}`}
    >
      Production Mode
    </Badge>
  );
});
