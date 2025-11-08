# Quickstart: Generator Control SPA

## Overview
This SPA provides operational control and visibility of data generators: monitor health, pause/resume, reset data safely, and inspect recent logs.

## Prerequisites
- Node.js 20+
- Yarn or npm
- Existing generator stack running (Docker Compose) exposing endpoints on `http://localhost:18000`

## Install
```bash
cd frontend
npm install
```
(If using yarn: `yarn install`)

## Development
```bash
npm run dev
```
Opens on `http://localhost:5173` (default Vite port). Ensure backend allows CORS if ports differ.

## Scripts
- `npm run dev` – Start Vite dev server with HMR
- `npm run build` – Production build (outputs to `frontend/dist/`)
- `npm run preview` – Preview local production build
- `npm test` – Run unit tests (Vitest)

## Environment Variables
Create `.env` in `frontend/` if needed:
```
VITE_API_BASE=http://localhost:18000
VITE_LOGS_LIMIT=500
```
Defaults applied if unset.

## API Consumption
- Health: `GET /health` polled every 5s
- Status: `GET /status` polled every 10s
- Pause: `POST /pause`
- Resume: `POST /resume`
- Reset: `POST /clean` (only when paused)
- Logs: `GET /logs?limit=200` (on demand + optional refresh)

## Typical Workflow
1. Start generator stack: `docker compose up -d` (from repo root if integrated)
2. Run SPA: `npm run dev`
3. Observe health metrics auto-refresh
4. Click Pause → generator transitions to paused
5. Click Reset → confirm destructive action; data cleared
6. Click Resume → generation restarts
7. View Logs → inspect recent operational entries

## Reset Safeguards
- Disabled if status is running
- Requires explicit confirmation
- Does not auto-resume afterward

## Testing
```bash
npm test
```
Add component tests in `frontend/tests/` verifying:
- Health panel renders status & uptime
- Control actions invoke correct endpoints
- Logs viewer displays fetched entries

## Production Build & Serve
```bash
npm run build
```
Static assets in `dist/`. For Docker integration, a minimal nginx or static server container can mount `dist/`. Example Dockerfile snippet (future task):
```
FROM node:20-alpine AS build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install --omit=dev
COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
```

## Error Handling UX
- Toast notifications for success/failure of control actions
- Connection indicator when periodic health poll fails (shows retry attempts)
- Graceful fallback message in logs viewer if endpoint not implemented yet

## Accessibility Notes
- Status changes announced via aria-live region
- Buttons include descriptive labels and tooltips
- Color not sole indicator (icon + text + color)

## Future Enhancements (Out of Scope)
- Streaming logs via SSE/WebSocket
- Multi-generator detailed drill-down view
- Authentication / RBAC
- Dark mode toggle

## Reference
See OpenAPI contract at `specs/002-spa-control/contracts/openapi.yaml` for full response schema.
