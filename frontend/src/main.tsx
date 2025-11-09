import React, { useCallback, useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { FluentProvider, webLightTheme, webDarkTheme } from '@fluentui/react-components';
import { ErrorBoundary } from './components/ErrorBoundary';
import { ToastProvider } from './components/ToastProvider';
import { HealthPanel } from './components/HealthPanel';
import { LogsPanel } from './components/LogsPanel';
import { readThemePreference, writeThemePreference } from './styles/pref';
import { ThemeToggle } from './components/ThemeToggle';

export interface ThemeContextValue {
  mode: 'light' | 'dark';
  setMode: (m: 'light' | 'dark') => void;
}

export const ThemeContext = React.createContext<ThemeContextValue | undefined>(undefined);

function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [mode, setModeState] = useState<'light' | 'dark'>(() => readThemePreference());

  const setMode = useCallback((m: 'light' | 'dark') => {
    setModeState(m);
    writeThemePreference(m);
  }, []);

  // Sync if preference is externally modified (rare, but defensive)
  useEffect(() => {
    const stored = readThemePreference();
    if (stored !== mode) setModeState(stored);
  }, [mode]);

  const fluentTheme = mode === 'dark' ? webDarkTheme : webLightTheme;
  // Ensure the html element attribute reflects current mode for global CSS targeting
  useEffect(() => {
    try {
      document.documentElement.setAttribute('data-theme', mode);
    } catch {}
  }, [mode]);
  return (
    <ThemeContext.Provider value={{ mode, setMode }}>
      <FluentProvider theme={fluentTheme}>{children}</FluentProvider>
    </ThemeContext.Provider>
  );
}

function App() {
  return (
    <ThemeProvider>
      <ToastProvider>
        <ErrorBoundary>
          <div className="app-container" style={{ padding: '1rem', maxWidth: 1000, margin: '0 auto' }}>
            <div className="app-header">
              <h1 style={{ margin: 0 }}>Generator Control SPA</h1>
              <ThemeToggle />
            </div>
            <HealthPanel />
            <LogsPanel />
          </div>
        </ErrorBoundary>
      </ToastProvider>
    </ThemeProvider>
  );
}

createRoot(document.getElementById('root')!).render(<App />);
