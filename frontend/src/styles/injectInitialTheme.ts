// Inject minimal initial theme styles before React mounts to avoid flash
(function initTheme() {
  try {
    const KEY = 'app.theme';
    const raw = localStorage.getItem(KEY);
    const mode: 'light' | 'dark' = raw === 'dark' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', mode);
    const style = document.createElement('style');
    style.setAttribute('data-initial-theme', mode);
    // Apply initial background to both html and body to avoid partial theming prior to React hydration.
    style.textContent = mode === 'dark'
      ? 'html,body{background:#0f1115;color:#f5f7fa;transition:background-color .2s ease,color .2s ease;}'
      : 'html,body{background:#ffffff;color:#1a1d21;transition:background-color .2s ease,color .2s ease;}';
    document.head.appendChild(style);
  } catch {
    // Fail silent; React provider will handle actual theme.
  }
})();

export {}; // Side-effect only module
