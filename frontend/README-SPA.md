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

- `/health` generator health & metrics
- `/status` lifecycle status (same shape as health simplified)
- `/pause` POST pause execution
- `/resume` POST resume execution
- `/clean` POST reset data (requires paused)
- `/logs` GET recent structured log entries (supports `limit`, `since`, `level`)

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

