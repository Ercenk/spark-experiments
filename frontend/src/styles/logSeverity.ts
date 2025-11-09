import { AppTheme } from './theme';
import { SeverityRole } from './tokens';

export interface SeverityStyle {
  borderColor: string;
  background: string;
  color: string;
  fontWeight: number;
}

export function getSeverityStyles(theme: AppTheme, role: SeverityRole): SeverityStyle {
  const m = theme.palette.severity[role];
  return {
    borderColor: m.accent,
    background: m.bg,
    color: m.text,
    fontWeight: role === 'down' ? 700 : role === 'degraded' ? 600 : 500,
  };
}
