import React, { useContext } from 'react';
import { Button } from '@fluentui/react-components';
import { ThemeContext } from '../main';

export const ThemeToggle: React.FC = () => {
  const ctx = useContext(ThemeContext);
  if (!ctx) return null;
  const { mode, setMode } = ctx;
  const next = mode === 'light' ? 'dark' : 'light';
  return (
    <Button appearance="secondary" onClick={() => setMode(next)}>
      {mode === 'light' ? 'Dark Mode' : 'Light Mode'}
    </Button>
  );
};
