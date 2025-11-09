# Generator Control SPA

Single-page application for monitoring and controlling data generators.

## Scripts
- `npm run dev` start development server
- `npm run build` production build
- `npm run preview` preview production build
- `npm test` run unit tests

## Tech Stack
React 18, Vite 5, TypeScript 5, Fluent UI, Axios, Zod.

Refer to quickstart at `specs/002-spa-control/quickstart.md`.

## Configuration

`VITE_API_BASE` sets the base URL for API requests (default fallback `http://localhost:18000`).

Development: `.env.development`
```
VITE_API_BASE=http://localhost:18000
```
Production: `.env.production` (can be overridden at build time via `--build-arg VITE_API_BASE=`)

## Docker

Multi-stage Dockerfile builds static assets then serves via nginx.

Build image manually:
```
docker build -t generator-frontend --build-arg VITE_API_BASE=http://localhost:18000 .
```

Compose service `frontend` exposes UI at http://localhost:19000

## Endpoints Consumed

Legacy endpoints (without `/api/` prefix) are being deprecated in favor of decoupled, read-only health + lifecycle/action handlers served under `/api/*`.

Preferred new endpoints:
- `/api/health` generator health (read-only, no side effects)
- `/api/pause` POST pause execution
- `/api/resume` POST resume execution (ensures baseline if missing)
- `/api/clean` POST reset data (requires paused)
- `/api/logs` GET recent structured log entries (supports `limit`, `since`, `level`)

Deprecated legacy endpoints (now return 410):
- `/health`, `/pause`, `/resume`, `/clean`, `/logs`

### /logs Features
| Name  | Description | Example |
|-------|-------------|---------|
| limit | Max entries (<=1000) | `?limit=200` |
| since | ISO8601 return entries after timestamp (used for pagination via `nextSince`) | `?since=2025-11-08T10:00:00Z` |
| level | Filter level (`info|warning|error`) | `?level=error` |

Response shape (includes pagination pointer):
```
{
	"entries": [ { "ts": "...", "level": "info", "message": "...", "source": "orchestrator", "context": { ... } } ],
	"totalReturned": 50,
	"nextSince": "2025-11-08T09:55:00.123Z"
}
```

## Development Notes

- Polling interval for health: 5s (see `HealthPanel`).
- Logs panel supports level filtering, auto-refresh, and incremental paging via `Load More` using `nextSince`.
- Control actions (pause/resume/reset) optimistically refresh health state.
- Layout: The `LogsPanel` now flex-grows to occupy remaining vertical space in the viewport (`.app-container` uses a column flex layout). Scroll behavior is handled by `.logs-panel-entries` with `overflow-y: auto`.

## Styling & Theming (Tokens)

Design tokens live in `src/styles/tokens.ts` (spacing, typography, elevation, radii). Theme palettes (light/dark) in `src/styles/theme.ts` with severity role colors. Common usage pattern:

```ts
import { spacing, typography } from '../styles/tokens';
import { getTheme } from '../styles/theme';
```

Severity styles consumed via `getSeverityStyles(theme, role)` from `src/styles/logSeverity.ts` for non-color cues (border accent + fontWeight). Contrast helper (`contrast.ts`) provides `contrastRatio` & `assertContrast` for accessibility guard rails.

Preference persistence key: `app.theme` (read/write via `pref.ts`). A future toggle component will set and store the mode before re-render.

## Contract Tests

Live endpoint contract tests in `tests/contract/*Contract.test.ts` validate health, logs, lifecycle, and clean endpoints against Zod schemas. They auto-skip if the generator is not running locally (ECONNREFUSED) to avoid CI false negatives.

## Error Handling & Retries

## Migration Notes

Services now exclusively use `/api/*` endpoints. Legacy fallbacks have been removed; frontend expects blueprint to be mounted.

`apiErrors.ts` normalizes failures into `ApiError` objects; logs fetch implements simple exponential backoff (2 retries) for transient network/5xx errors.


