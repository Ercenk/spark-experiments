## Operations API (Decoupled)

Use the new `/api` prefix for all control and health queries.

### Health Snapshot
```
curl http://localhost:18000/api/health | jq
```

### Pause & Resume
```
curl -X POST http://localhost:18000/api/pause
curl -X POST http://localhost:18000/api/resume
```
On resume the system ensures baseline data (companies + first driver batch) if missing.

### Data Reset (Requires Paused)
```
curl -X POST http://localhost:18000/api/clean
```

### Logs Retrieval
```
curl "http://localhost:18000/api/logs?limit=50&level=error" | jq
```

Recommended frontend migration strategy: try `/api/*` first, fallback to legacy endpoints only if 410 not returned.

# Quickstart: SPA Styling Refinement

## Prerequisites
- Node.js 18+
- Existing repository cloned
- Installed dependencies (`npm install` inside `frontend/`)

## Steps
1. Checkout feature branch:
   ```bash
   git checkout 001-spa-styling
   ```
2. Create token file (will be added in implementation): `frontend/src/styles/tokens.ts`.
3. Add theme provider wrapper in `main.tsx` importing tokens and reading `localStorage` key `app.theme`.
4. Introduce severity styles in `styles/logSeverity.css` (or ts module) mapping roles.
5. Run dev server:
   ```bash
   cd frontend
   npm run dev
   ```
6. Toggle theme in UI; confirm persistence after reload.
7. Run tests including accessibility:
   ```bash
   npm test
   ```

## Validation
- Contrast audit passes (axe rules: color-contrast) with zero violations.
- Theme toggle no layout shift > 0.1 cumulative.
- Logs severity visually distinguished via color + weight + border accent.

## Troubleshooting
- Missing theme on first paint: ensure localStorage read occurs before initial render (guard with early state initialization).
- Contrast failures: adjust token hex values; rerun tests.
- Flicker between themes: verify CSS variables injected synchronously in provider.
