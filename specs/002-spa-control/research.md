# Research & Decisions: Generator Control SPA

**Branch**: 002-spa-control  
**Date**: 2025-11-08

## Clarifications Resolved

1. **Log Retention Window**  
   - Decision: Client will request at most the latest 500 entries or entries newer than 10 minutes (whichever smaller) using query params `?limit=500&since=<ISO8601>`.
   - Rationale: Avoid large payloads while satisfying visibility (SC-007, SC-008).  
   - Alternatives: (a) Fixed count only (less temporal control), (b) Time window only (risk of huge payload after burst). Hybrid chosen.

2. **Reset Auto-Resume Behavior**  
   - Decision: Reset does NOT auto-resume generation. User must explicitly resume.  
   - Rationale: Aligns with safety principle; destructive operation followed by explicit reactivation prevents accidental data churn.  
   - Alternatives: Auto-resume (risk of accidental generation) / Configurable flag (adds complexity for minimal benefit).

3. **Aggregated Severity Representation**  
   - Decision: Present a single overall status (running, paused, degraded) + per-generator panels (future extension). Initially only running/paused implemented.  
   - Rationale: Current backend surfaces a unified lifecycle. Extensible path for later multi-generator detail without UI rework.  
   - Alternatives: Implement full per-generator matrix now (premature, no data variety yet).

## Technology Selections

| Area | Decision | Rationale | Alternatives Considered |
|------|----------|-----------|--------------------------|
| Build Tool | Vite 5 | Fast dev HMR, minimal config | CRA (deprecated), Webpack (heavier), Parcel (similar but less ecosystem momentum) |
| UI Library | Microsoft Fluent UI (@fluentui/react-components) | Consistent accessible components, professional styling | MUI (heavier), Chakra (different design language), Tailwind (lower-level) |
| HTTP Client | Axios | Interceptors, widespread patterns | Fetch API (manual boilerplate), Ky (smaller but less common) |
| Validation | Zod | Runtime + TS inference synergy | Yup (weaker TS), io-ts (more verbose) |
| State Mgmt | Local component + React Context | Simplicity, single page, limited shared state | Redux (overhead), Zustand (unnecessary), Recoil (adds complexity) |
| Testing | Vitest + RTL | Vite integration, fast | Jest (fine but slower in this stack) |
| Logs Retrieval | Polling (5–10s) + on-demand refresh | Simplicity vs SSE/WebSockets | SSE (infra change), WebSocket (overkill), Long-poll (unnecessary) |

## API Design Decisions

### Logs Endpoint (`GET /api/logs`)
Parameters:
- `limit` (int, default 200, max 500)
- `since` (ISO 8601 timestamp, optional)
- `level` (enum: info|warning|error, optional)

Response:
```json
{
  "entries": [
    {"ts": "2025-11-08T21:30:12Z", "level": "info", "message": "Batch generated", "source": "company"}
  ],
  "nextSince": "2025-11-08T21:30:12Z"
}
```

Decision: Provide `nextSince` for incremental fetching (future optimization). Initial implementation may ignore if not needed by UI.

### Health
- UI consumes `/api/health` (single unified snapshot) polled every 5s. All root endpoints removed.

### Control Actions
- All POST actions return uniform `ControlResult` shape: `{ "success": true, "action": "pause", "timestamp": "...", "status": "paused" }`.
- Decision: UI will treat any non-2xx as failure and surface toast with error message.

## Performance Considerations
- DOM virtualization not required (<500 log rows). If volume grows, integrate windowing (e.g., react-virtuoso) later.
- Avoid global re-renders by isolating polling state in context and passing derived props to components.
- Keep bundle lean: no icon packs beyond Fluent defaults.

## Accessibility & UX
- Fluent UI baseline accessibility leveraged.
- Live region (aria-live="polite") for status changes (pause/resume confirmations).
- Color + icon + text for states (avoid color-only differentiation).

## Security Considerations
- Internal tool; no auth for now. Document hardening path: add reverse proxy enforcing Basic/OIDC later.
- CORS assumption: SPA served from same origin (prefer) or enable simple CORS on backend if separate port.

## Open Questions (Defer)
- Streaming logs (SSE) if operators require sub-second latency. Defer until need emerges.
- Multi-generator granularity once more generator types exist.

## Decision Log (Summary Format)

| Decision | Rationale | Alternatives | Status |
|----------|-----------|-------------|--------|
| Poll logs endpoint | Easiest to implement; sufficient latency | SSE, WebSocket | Accepted |
| No auto-resume after reset | Safety & explicit control | Auto-resume | Accepted |
| Fluent UI adoption | Accessibility + consistency | MUI, Chakra, Tailwind | Accepted |
| Zod for validation | TS inference synergy | Yup, io-ts | Accepted |
| Single page only | Scope control | Multi-route layout | Accepted |

All prior NEEDS CLARIFICATION items resolved; no blockers for Phase 1 design.
