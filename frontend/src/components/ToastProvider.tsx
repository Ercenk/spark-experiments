import React, { createContext, useContext, useState, useCallback } from 'react';
import { ToastMessage } from '../state/types';
import { Button } from '@fluentui/react-components';

interface ToastContextValue {
  messages: ToastMessage[];
  showSuccess: (text: string) => void;
  showError: (text: string) => void;
  showInfo: (text: string) => void;
  dismiss: (id: string) => void;
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined);

function makeMessage(type: ToastMessage['type'], text: string): ToastMessage {
  return { id: Math.random().toString(36).slice(2), type, text };
}

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [messages, setMessages] = useState<ToastMessage[]>([]);

  const push = useCallback((m: ToastMessage) => {
    setMessages((prev) => [...prev, m]);
    setTimeout(() => {
      setMessages((prev) => prev.filter((x) => x.id !== m.id));
    }, 5000);
  }, []);

  const showSuccess = useCallback((text: string) => push(makeMessage('success', text)), [push]);
  const showError = useCallback((text: string) => push(makeMessage('error', text)), [push]);
  const showInfo = useCallback((text: string) => push(makeMessage('info', text)), [push]);
  const dismiss = useCallback((id: string) => setMessages((prev) => prev.filter((m) => m.id !== id)), []);

  return (
    <ToastContext.Provider value={{ messages, showSuccess, showError, showInfo, dismiss }}>
      {children}
      <div style={{ position: 'fixed', top: 8, right: 8, display: 'flex', flexDirection: 'column', gap: '8px', zIndex: 1000 }}>
        {messages.map((m) => (
          <div
            key={m.id}
            style={{
              padding: '8px 12px',
              borderRadius: 4,
              background: m.type === 'error' ? '#d13438' : m.type === 'success' ? '#107c10' : '#6264a7',
              color: '#fff',
              minWidth: 240,
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>{m.text}</span>
              <Button appearance="transparent" size="small" onClick={() => dismiss(m.id)}>×</Button>
            </div>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within ToastProvider');
  return ctx;
}
