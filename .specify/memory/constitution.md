<!--
Sync Impact Report
Version: 0.1.0 -> 0.2.0 (MINOR: new principle added)
Modified Principles: (none)
Added Sections: Principle VI - Strict Python Type Safety
Removed Sections: (none)
Templates Alignment:
	.specify/templates/plan-template.md ✅ (Constitution Check will reference type safety principle)
	.specify/templates/spec-template.md ✅ (Independent user stories unaffected)
	.specify/templates/tasks-template.md ✅ (Task grouping by story unchanged)
Deferred TODOs: None
Rationale: Adding strict type checking enforcement for Python code quality, maintainability, and early error detection.
-->

# Spark Transportation Ingestion Sandbox Constitution

## Core Principles

### I. Reproducible Local-First Spark Cluster
All Spark experiments MUST run exclusively via a versioned Docker Compose
definition that provisions the local multi-node Spark cluster (driver +
executors) and any auxiliary services (e.g., mock data generators). Manual
container mutation, ad-hoc port remapping, or persistence of state outside
Compose volumes is PROHIBITED. Every experiment MUST be runnable from a clean
clone with: `docker compose up` followed by a documented single entrypoint.
Cluster configuration (Spark conf, JVM opts) MUST be declared, never edited
in-place. Environments MUST tear down cleanly (`docker compose down -v`) after
experiment completion.

### II. Data Realism & Synthetic Fidelity
Ingestion pipelines MUST use either (a) licensed sample transportation datasets
with documented source + license metadata or (b) synthetic datasets generated
by reproducible scripts whose schema, generation parameters, record count and
random seeds are recorded in an accompanying `dataset.md`. Synthetic data MUST
approximate realistic distributions (e.g., GPS jitter, trip durations). Any
external dataset introduction without provenance metadata is BLOCKED. Schema
changes MUST trigger regeneration + version bump of the dataset manifest.

### III. Iterative Experiment Discipline
Each Spark experiment MUST declare a concise hypothesis, input dataset
snapshot reference (immutable path or checksum), transformation plan, expected
metrics (e.g., records/sec, shuffle read size, median latency), and success
criteria inside an `experiment.yaml` or `experiment.md`. Implementation only
begins after the hypothesis file exists. Results (metrics + narrative outcome)
MUST be appended immutably; post-result code changes require creating a new
experiment directory (e.g., `exp-002`). Experiments live under `/experiments`
and MUST be sequentially numbered.

### IV. Observability & Metrics
All Spark jobs MUST emit structured JSON Lines logs capturing: timestamp,
stage id, records processed, input bytes, output bytes, executor CPU %, GC
time, and error details (if any). Metrics MUST be derivable locally without
external SaaS dependencies. Failures MUST log a minimal data sample (redacted
PII) aiding triage. A human-readable summary MAY be produced but does not
replace structured logs. Absence of metrics blocks experiment acceptance.

### V. Simplicity & Teardown Hygiene
Complexity MUST be justified by learning value. Prefer minimal transformations
and avoid premature optimization (e.g., caching, partition tuning) until a
baseline metric is recorded. Adding new services (e.g., Kafka mock) requires
a rationale in the experiment hypothesis. Unused containers, volumes, and
datasets MUST be removed after experiments. Code MUST favor clarity over
micro-optimizations. Justifications for retained complexity go into
`complexity.md` at repo root if recurring.

### VI. Strict Python Type Safety
All Python source files MUST use comprehensive type annotations for function
signatures (parameters and return types), class attributes, and module-level
variables. Type hints MUST follow PEP 484 conventions using standard library
`typing` module constructs (e.g., `List[str]`, `Optional[int]`, `Dict[str, Any]`).
Generic types MUST be fully parameterized (no bare `list`, `dict`). Type checking
MUST be enforced via `mypy` in strict mode (`--strict` flag) with zero errors
tolerated in CI/CD pipeline or pre-commit hooks. New code without type annotations
is BLOCKED from merge. Existing untyped code MUST be annotated incrementally;
exemptions require explicit `# type: ignore[error-code]` comments with
justification. Rationale: Type safety prevents entire classes of runtime errors,
improves IDE support, enables confident refactoring, and serves as executable
documentation for data generator schemas and Spark transformation pipelines.

## Environment & Data Constraints

Docker Compose is the canonical orchestration. Spark image MUST pin exact
version (e.g., `apache/spark:3.5.0`); upgrading versions triggers a new experiment to
compare performance deltas. Resource allocation (driver/executor memory/cores)
MUST be explicitly declared; implicit defaults prohibited. Local filesystem
storage under `/data` MUST separate raw, staged, and processed zones.
Data retention: synthetic datasets MAY be deleted after metric capture if
artifact integrity (checksum + schema) stored. External datasets MUST retain
original unmodified copy. All schemas MUST be versioned (`schema-vX.Y.json`).

## Development Workflow & Review Gates

1. Author experiment hypothesis + dataset manifest → REVIEW (check principles).
2. Implement Spark job inside numbered experiment directory.
3. Capture metrics + structured logs → REVIEW (validate Observability).
4. Document results + learning outcomes → MERGE.
5. Complexity added? Provide justification; reviewer enforces Principle V.

Pull requests MUST include: experiment id, hypothesis file path, dataset
manifest reference, expected vs actual metrics table. Reviewers MUST deny if
**Version**: 0.2.0 | **Ratified**: 2025-11-08 | **Last Amended**: 2025-11-08

## Governance

This constitution supersedes ad-hoc practices. Amendments require: (a) change
proposal PR describing rationale + impact, (b) version bump per semantic rules,
and (c) confirmation that plan/spec/tasks templates remain aligned. Versioning:
MAJOR = removal or redefinition of a principle; MINOR = new principle or
section; PATCH = wording clarity without altering enforcement meaning.
Quarterly (or after every 5 experiments) a compliance sweep MUST verify: all
experiment directories contain required hypothesis + results + metrics; Docker
Compose unchanged except through reviewed PRs. Non-compliance MUST be remediated
before new experiments begin.

**Version**: 0.1.0 | **Ratified**: 2025-11-08 | **Last Amended**: 2025-11-08
