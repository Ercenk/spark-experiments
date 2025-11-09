import { SeverityRole, radii } from './tokens';

interface Palette {
  bg: string;
  bgAlt: string;
  text: string;
  textAlt: string;
  border: string;
  accent: string;
  focus: string;
  danger: string;
  warning: string;
  success: string;
  severity: Record<SeverityRole, { text: string; bg: string; accent: string }>;
}

export interface AppTheme {
  name: 'light' | 'dark';
  palette: Palette;
}

export const lightTheme: AppTheme = {
  name: 'light',
  palette: {
    bg: '#ffffff',
    bgAlt: '#f5f7fa',
    text: '#1a1d21',
    textAlt: '#4b5260',
    border: '#d0d5dc',
    accent: '#2563eb',
    focus: '#9333ea',
    danger: '#dc2626',
    warning: '#f59e0b',
    success: '#16a34a',
    severity: {
      healthy: { text: '#166534', bg: '#dcfce7', accent: '#22c55e' },
      degraded: { text: '#92400e', bg: '#fef3c7', accent: '#f59e0b' },
      down: { text: '#991b1b', bg: '#fee2e2', accent: '#dc2626' },
      unknown: { text: '#374151', bg: '#e5e7eb', accent: '#6b7280' },
    },
  },
};

export const darkTheme: AppTheme = {
  name: 'dark',
  palette: {
    bg: '#0f1115',
    bgAlt: '#1b1f24',
    text: '#f5f7fa',
    textAlt: '#d1d5db',
    border: '#374151',
    accent: '#3b82f6',
    focus: '#c084fc',
    danger: '#ef4444',
    warning: '#fbbf24',
    success: '#22c55e',
    severity: {
      healthy: { text: '#22c55e', bg: '#14532d', accent: '#16a34a' },
      degraded: { text: '#f59e0b', bg: '#78350f', accent: '#d97706' },
      down: { text: '#dc2626', bg: '#7f1d1d', accent: '#b91c1c' },
      unknown: { text: '#9ca3af', bg: '#374151', accent: '#6b7280' },
    },
  },
};

export function getTheme(name: 'light' | 'dark'): AppTheme {
  return name === 'dark' ? darkTheme : lightTheme;
}

export const commonStyles = {
  panel: {
    borderRadius: radii.md,
    transition: 'background-color 200ms ease',
  }
};
