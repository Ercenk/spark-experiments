const KEY = 'app.theme';
export function readThemePreference(): 'light' | 'dark' {
  try {
    const v = localStorage.getItem(KEY);
    if (v === 'dark' || v === 'light') return v;
  } catch {}
  return 'light';
}
export function writeThemePreference(mode: 'light' | 'dark') {
  try { localStorage.setItem(KEY, mode); } catch {}
}
