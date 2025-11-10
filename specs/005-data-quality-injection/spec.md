# Feature Specification: Data Quality Injection

**Feature Branch**: `005-data-quality-injection`  
**Created**: 2025-11-09  
**Status**: Draft  
**Input**: User description: "Inject errors, missing data etc to the original data generation simulation so I can manage missing data etc, to simulate data cleansing."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configurable Data Quality Issues (Priority: P1)

Data engineer needs to inject realistic data quality issues (missing fields, nulls, malformed values) into generated driver events and company records with configurable probabilities to validate that the medallion pipeline correctly identifies, flags, and handles bad data.

**Why this priority**: Without realistic dirty data, the data quality validation and cleansing logic in the pipeline cannot be properly tested or demonstrated.

**Independent Test**: Run generators with quality issue injection enabled; verify specified percentage of records contain configured defects; confirm defects are diverse and realistic.

**Acceptance Scenarios**:

1. **Given** quality injection configured at 10% error rate, **When** generator runs, **Then** approximately 10% of generated records contain at least one quality issue.
2. **Given** specific error types disabled in config, **When** generator runs, **Then** those error types do not appear in generated data.
3. **Given** quality injection disabled, **When** generator runs, **Then** all records are clean (baseline behavior preserved).

---

### User Story 2 - Traceable Quality Issue Metadata (Priority: P2)

Operations and data engineering teams need to see which specific quality issues were injected into each record (via logs or metadata) to correlate pipeline rejection reasons with known injected defects during testing and validation.

**Why this priority**: Enables verification that pipeline is catching the right issues; provides audit trail for testing.

**Independent Test**: Review injection logs or metadata; confirm each injected issue is logged with record ID, issue type, and field affected.

**Acceptance Scenarios**:

1. **Given** records with injected quality issues, **When** reviewing injection logs, **Then** each issue is logged with record identifier, issue type, and affected field.
2. **Given** pipeline rejects records, **When** cross-referencing with injection logs, **Then** rejection reasons align with injected defects.

---

### User Story 3 - Diverse Issue Types Coverage (Priority: P2)

Data quality testing requires diverse realistic defects including: missing required fields, null values, malformed timestamps, invalid enumerations, duplicates, schema violations, and boundary condition violations.

**Why this priority**: Comprehensive testing requires coverage of multiple failure modes that occur in production systems.

**Independent Test**: Enable all issue types; verify generator produces examples of each category; confirm variety within categories (e.g., different fields can be null, different timestamp formats malformed).

**Acceptance Scenarios**:

1. **Given** all issue types enabled, **When** sufficient records generated, **Then** examples of each issue type category appear in output.
2. **Given** field-level randomization, **When** reviewing injected issues, **Then** multiple different fields affected across records (not just same field repeatedly).

---

### Edge Cases

- Zero error rate configured (100% clean data) - generators behave normally
- 100% error rate configured - every record has at least one issue
- Conflicting issue types (e.g., missing field AND null value for same field) - one issue wins deterministically
- Issue injection in company onboarding vs driver events - both support injection independently
- Re-running with same seed - injected issues are reproducible
- Pipeline downstream cannot parse heavily corrupted records - malformed JSON still parseable as JSON Lines

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support configurable probability (0.0 to 1.0) for injecting data quality issues into generated records.
- **FR-002**: System MUST inject missing required fields (field omitted entirely from JSON) with configurable probability per field type.
- **FR-003**: System MUST inject null values for fields that should not be null with configurable probability.
- **FR-004**: System MUST inject malformed timestamp strings (invalid ISO8601 formats, unparseable values) with configurable probability.
- **FR-005**: System MUST inject invalid enumeration values for event_type and geography fields with configurable probability.
- **FR-006**: System MUST inject intentional duplicate records (same driver_id + timestamp) to test deduplication logic.
- **FR-007**: System MUST inject boundary violations (timestamps outside batch interval, future dates) with configurable probability.
- **FR-008**: System MUST log each injected quality issue with record identifier, issue type, affected field, and reason code.
- **FR-009**: System MUST preserve existing seed-based reproducibility (same seed + same error config = identical defect pattern).
- **FR-010**: System MUST allow independent configuration of error rates for driver events vs companies.
- **FR-011**: System MUST default to zero error rate (clean data) when quality injection not explicitly enabled.
- **FR-012**: System MUST ensure injected issues do not prevent JSON Lines parsing (malformed values are still valid JSON primitives).
- **FR-013**: System MUST support disabling specific issue types while keeping others enabled.
- **FR-014**: System MUST record aggregate quality issue statistics in batch metadata (counts per issue type).
- **FR-015**: System MUST inject issues post-generation deterministically using the same random seed as record generation.

### Key Entities

- **QualityInjectionConfig**: Configuration for error injection; attributes: enabled (bool), error_rate (float 0-1), issue_type_probabilities (dict), affected_entities (driver_events|companies|both).
- **InjectedIssue**: Record of a single injected defect; attributes: record_id, issue_type (missing_field|null_value|malformed_timestamp|invalid_enum|duplicate|boundary_violation), affected_field, original_value, injected_value, reason_code.
- **IssueType**: Enumeration of defect categories (missing_field, null_value, malformed_timestamp, invalid_enum, duplicate_record, boundary_violation, schema_mismatch).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Quality injection configured at 15% error rate produces 15% ± 2% defective records across 1000+ record sample.
- **SC-002**: All configured issue types appear in generated data when enabled (100% coverage of enabled types across sufficient sample).
- **SC-003**: Injection logs capture 100% of injected issues with complete metadata (no silent injections).
- **SC-004**: Pipeline correctly rejects ≥95% of injected quality issues during validation (confirms pipeline catches defects).
- **SC-005**: Re-running with identical seed and config produces byte-identical defect pattern (reproducibility maintained).
- **SC-006**: Disabling specific issue types (e.g., null_value) results in 0 occurrences of that type (selective control works).
- **SC-007**: Aggregate issue statistics in batch metadata match detailed injection logs (counts consistent).
- **SC-008**: Zero error rate configuration produces 0 quality issues across any sample size (clean baseline preserved).
