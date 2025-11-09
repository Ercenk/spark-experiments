// Spacing scale (pixels) – incremental rhythm
export const spacing = [0, 2, 4, 8, 12, 16, 20, 24, 32, 40];

// Typography tiers (semantic usage)
export interface TypographyTier { fontSize: string; lineHeight: string; weight: number; }
export const typography: Record<string, TypographyTier> = {
  display: { fontSize: '24px', lineHeight: '32px', weight: 600 },
  title: { fontSize: '20px', lineHeight: '28px', weight: 600 },
  section: { fontSize: '16px', lineHeight: '24px', weight: 600 },
  body: { fontSize: '14px', lineHeight: '20px', weight: 400 },
  monospace: { fontSize: '13px', lineHeight: '20px', weight: 400 },
  caption: { fontSize: '12px', lineHeight: '16px', weight: 400 },
};

// Severity roles used by logs & health styling
export const severityRoles = ['healthy','degraded','down','unknown'] as const;
export type SeverityRole = typeof severityRoles[number];

// Elevation (shadows) – simple depth scale
export const elevation = {
  low: '0 1px 2px rgba(0,0,0,0.06)',
  mid: '0 2px 4px rgba(0,0,0,0.08)',
  high: '0 4px 12px rgba(0,0,0,0.12)'
};

// Border radius scale
export const radii = { sm: '3px', md: '6px', lg: '10px' };

// Transition timing helpers
export const transitions = {
  fast: '120ms ease-out',
  base: '200ms ease',
  slow: '320ms ease-in'
};

// Z-index layering for future toast/theme overlay needs
export const layers = {
  base: 0,
  header: 10,
  overlay: 100,
  toast: 1000
};
