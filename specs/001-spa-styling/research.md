# research.md - SPA Styling & Operations Decoupling

## Unknowns Resolution

### Polling Interval for Health
- Decision: Use 3s default polling interval with exponential backoff to 5s if unchanged snapshot for 5 consecutive polls.
- Rationale: Balances UI freshness with reduced needless generator interference; 3s below typical human perception of staleness (>5s often noticed).
- Alternatives considered: Fixed 2s (higher overhead), adaptive based on batch rate (complexity not justified yet).

### Future Authentication Layer
- Decision: Defer authentication; design handlers with clear separation allowing later middleware injection.
- Rationale: Local sandbox scope; premature auth adds friction.
- Alternatives: Basic API key header (unnecessary now), mTLS (overkill locally).

### OpenAPI Location Strategy
- Decision: Introduce new spec file for decoupled operations: `specs/001-spa-styling/contracts/openapi.yaml` referencing existing schemas where stable; keep old file for backward compatibility until migration complete.
- Rationale: Avoid disruptive edits to active control feature branch; enables parallel evolution.
- Alternatives: Single merged spec (risk of merge noise), incremental edits on original (semantic coupling).

### Spark Metrics Inclusion in Health
- Decision: Exclude raw Spark executor metrics for now; health remains generator-focused plus batch counters.
- Rationale: Styling feature scope; adding metrics expands payload & styling complexity.
- Alternatives: Lightweight summary (CPU%), but requires new collection pipeline.

### Baseline Generation Retry Backoff
- Decision: Implement linear backoff: retry baseline init up to 3 times at 1s, 2s, 3s intervals before marking degraded.
- Rationale: Simple, observable progression; low complexity.
- Alternatives: Exponential (overkill for 3 attempts), constant (less resilient under transient FS delay).

## Best Practices & Patterns

### Router & Handlers Design (Flask)
- Decision: Use Blueprint `api` + modular handler functions grouped by concern: `health.py` (read-only), `lifecycle.py` (pause/resume), `data_reset.py` (clean), `logs.py` (retrieval).
- Rationale: Clear separation of query vs command paths; reduces God object risk.
- Alternatives: Class-based view per resource (adds boilerplate), single file routes (scales poorly).

### Service Layer Abstractions
- Decision: Introduce services directory with: `health_aggregator.py`, `lifecycle_service.py`, `baseline_initializer.py`, `verification_service.py`, `log_reader.py`.
- Rationale: Encapsulates logic; unit-testable without Flask context.
- Alternatives: Keep logic inside handlers (mixed concerns, harder to test).

### Action & Verification Logging Format
- Decision: Use structured dicts aggregated into response JSON; avoid string token parsing.
- Rationale: Machine-readability → simpler frontend mapping.
- Alternatives: Semi-colon token string list (fragile parsing), separate endpoint (extra round-trip).

### Type Safety Enforcement
- Decision: All new modules fully annotated; add mypy strict enforcement to CI for `src/generators/services/*`.
- Rationale: Constitution Principle VI compliance.
- Alternatives: Gradual typing (slows reliability goals), docs-only (non-enforceable).

## Decisions Summary Table

| Topic | Decision | Rationale | Alternatives |
|-------|----------|-----------|-------------|
| Polling interval | 3s + backoff | Balance freshness & overhead | Fixed 2s; adaptive rate |
| Auth layer | Defer | Local-only scope | API key; mTLS |
| OpenAPI location | New file | Isolated evolution | Merge into existing |
| Spark metrics | Exclude now | Keep scope tight | Include partial metrics |
| Baseline backoff | Linear 1/2/3s | Simplicity | Exponential; constant |
| Router style | Blueprint + modules | Separation of concerns | Single file; class views |
| Service layer | Introduce services/ | Testability | Handler logic only |
| Logging format | Structured dicts | Machine readability | Token strings |
| Type safety | Strict annotations | Constitution compliance | Gradual typing |

## Rationale Highlights
- Separation improves maintainability and supports future scaling of ops features.
- Structured responses lower frontend parsing complexity and reduce failure modes.
- Backoff strategy chosen for transparency during manual observation.

## Pending Risks
- Dual OpenAPI specs risk divergence → plan migration task after validation.
- Added modules increase surface area; enforce tests to prevent dead code.

## Next Steps
1. Define data model entities in `data-model.md`.
2. Draft new OpenAPI spec with separated tags.
3. Implement quickstart reflecting new router & handlers.
4. Update plan constitution check post-design.
