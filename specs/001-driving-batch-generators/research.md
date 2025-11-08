# Research & Clarifications: Driving Batch Generators

**Date**: 2025-11-08  
**Related Plan**: ./plan.md  
**Outstanding Clarifications Addressed Below**: Delta Lake version, ADLS emulation layout names, scheduling mechanism.

## Open Questions (from Technical Context)

| ID | Topic | Original Note | Resolution Status |
|----|-------|---------------|-------------------|
| Q1 | Delta Lake Version | Pin explicit version? | Resolved |
| Q2 | ADLS Directory Layout | raw/staged/processed/manifests naming? | Resolved |
| Q3 | Scheduling Mechanism | Structured Streaming vs cron loop vs external orchestrator | Resolved |

## Decisions

### D1: Delta Lake Version
- **Decision**: Use `delta-spark` 2.4.x (compatible with Spark 3.5.0; stable APIs) with Apache Spark official image.  
- **Rationale**: Matches Spark 3.5 line; avoids breaking changes introduced in 3.x preview features; widely adopted. Apache Spark official image provides more control over Spark configuration.  
- **Alternatives Considered**: Latest (risk of incompat), 2.3.x (older, fewer features).  
- **Follow-up**: Pin exact minor in requirements file when added.

### D2: ADLS Emulation Directory Layout
- **Decision**: Adopt four zones: `raw/`, `staged/`, `processed/`, `manifests/`.  
- **Rationale**: Mirrors common medallion-inspired staging while keeping initial scope simple; manifests isolated for quick listing; supports later bronze/silver/gold mapping if needed.  
- **Alternatives**: bronze/silver/gold naming (premature semantic commitment), single flat directory (loses lineage clarity).  
- **Follow-up**: Document zone semantics in quickstart.

### D3: Scheduling Mechanism
- **Decision**: Implement a lightweight Python scheduler loop inside generator container for 15-min interval, writing batch directories; no Spark Structured Streaming initial use.  
- **Rationale**: Keeps complexity low; Structured Streaming would add overhead for local learning goals; we only need discrete batch artifacts.  
- **Alternatives**: Cron in container (less flexible for test triggering), Spark Structured Streaming (higher complexity), external orchestrator (out of scope).  
- **Follow-up**: Provide manual immediate trigger CLI (`--now`) fulfilling FR-013.

## Additional Best Practices Notes
- **Logging**: Use JSON Lines; include run_id, seed, interval_start, interval_end for correlation.
- **Reproducibility**: All generators accept explicit `--seed`; if omitted, generate and persist seed in manifest.
- **Resource Sizing**: Single executor with 1-2 cores sufficient; scale test later by adjusting `docker-compose.yml`.
- **Data Validation**: Schema assertion before writing Delta tables; fail fast if mismatch.

## Impact on Constitution Gates
- All unresolved items now clarified; initial gate evaluation remains PASS.  
- Observability spec strengthened with run_id inclusion.

## Summary
All NEEDS CLARIFICATION markers resolved; plan may proceed to Phase 1 design artifacts.
