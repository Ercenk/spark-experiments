import { makeStyles, shorthands, tokens } from '@fluentui/react-components';

/**
 * Fluent UI token-based styles for generation mode indicators
 * Feature 007: Emulated mode display
 */
export const useModeStyles = makeStyles({
  emulatedBadge: {
    backgroundColor: tokens.colorPaletteYellowBackground2,
    color: tokens.colorPaletteYellowForeground1,
    ...shorthands.border('2px', 'solid', tokens.colorPaletteYellowBorder1),
    fontWeight: tokens.fontWeightSemibold,
  },
  productionBadge: {
    backgroundColor: tokens.colorNeutralBackground1,
    color: tokens.colorNeutralForeground1,
    ...shorthands.border('1px', 'solid', tokens.colorNeutralStroke1),
  },
});
