import React from 'react';
import { createRoot } from 'react-dom/client';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { ErrorBoundary } from './components/ErrorBoundary';
import { ToastProvider } from './components/ToastProvider';
import { HealthPanel } from './components/HealthPanel';
import { LogsPanel } from './components/LogsPanel';

function App() {
  return (
    <FluentProvider theme={webLightTheme}>
      <ToastProvider>
        <ErrorBoundary>
          <div style={{ padding: '1rem', maxWidth: 1000, margin: '0 auto' }}>
            <h1>Generator Control SPA</h1>
            <HealthPanel />
            <LogsPanel />
          </div>
        </ErrorBoundary>
      </ToastProvider>
    </FluentProvider>
  );
}

createRoot(document.getElementById('root')!).render(<App />);
