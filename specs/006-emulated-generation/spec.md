# Feature Specification: Emulated Fast-Cadence Data Generation

**Feature Branch**: `006-emulated-generation`  
**Created**: 2025-11-09  
**Status**: Draft  
**Input**: User description: "emulated data generation should be in seconds and smaller batches to visualize and follow closely the whole pipeline process"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Observe Real-Time Data Flow (Priority: P1)

As a data pipeline developer, I want to generate small batches of data every few seconds so that I can observe the complete medallion pipeline (bronze → silver → gold) in near real-time and verify transformations are working correctly without waiting for production-scale batch intervals.

**Why this priority**: Core MVP functionality enabling rapid feedback during pipeline development. Without fast cadence, developers waste time waiting 15+ minutes between batches to verify changes.

**Independent Test**: Can be fully tested by starting emulated mode, observing batch generation every 5-10 seconds, and confirming data appears in bronze within seconds of generation.

**Acceptance Scenarios**:

1. **Given** emulated mode is enabled, **When** the generator starts, **Then** company onboarding batches are generated every 5-10 seconds instead of hourly
2. **Given** emulated mode is running, **When** observing the event stream, **Then** driver event batches are generated every 5-10 seconds instead of every 15 minutes
3. **Given** multiple batches have been generated in emulated mode, **When** inspecting batch metadata, **Then** each batch contains 5-20 records instead of hundreds/thousands
4. **Given** emulated mode is active, **When** viewing logs, **Then** timestamps show batches completing within seconds of each other

---

### User Story 2 - Toggle Between Production and Emulated Modes (Priority: P2)

As a data pipeline developer, I want to easily switch between production-scale generation (large batches, realistic intervals) and emulated fast-cadence generation (small batches, second-level intervals) so that I can use the same codebase for both development/testing and production scenarios.

**Why this priority**: Prevents code duplication and ensures emulated mode accurately represents production logic, just at different scale/speed.

**Independent Test**: Can be fully tested by toggling configuration setting and observing batch size and interval changes without code modifications.

**Acceptance Scenarios**:

1. **Given** configuration file set to production mode, **When** generator starts, **Then** batches use production intervals (hourly, 15-min) and sizes (100+ companies, 1000+ events)
2. **Given** configuration file set to emulated mode, **When** generator starts, **Then** batches use fast intervals (5-10 seconds) and small sizes (5-20 records)
3. **Given** switching from production to emulated mode, **When** generator restarts, **Then** no code changes are required, only configuration update
4. **Given** emulated mode configuration, **When** examining generated data schemas, **Then** schemas remain identical to production mode (only volume/timing differs)

---

### User Story 3 - Visualize Pipeline Progress in Dashboard (Priority: P3)

As a data pipeline developer, I want to see real-time metrics in the web dashboard showing batch counts, processing times, and quality statistics updated every few seconds so that I can immediately spot issues without manually checking log files.

**Why this priority**: Enhances developer experience but depends on fast data generation (P1) and existing dashboard infrastructure.

**Independent Test**: Can be fully tested by opening dashboard while emulated generation runs and confirming metrics update every 5-10 seconds with new batch data.

**Acceptance Scenarios**:

1. **Given** emulated generation is running, **When** dashboard is open, **Then** batch counter increments every 5-10 seconds
2. **Given** batches contain quality issues, **When** viewing dashboard quality panel, **Then** corrupted record percentages update in real-time
3. **Given** pipeline is processing batches, **When** observing dashboard, **Then** processing latency metrics (bronze→silver→gold) are visible and current
4. **Given** emulated mode batch completes, **When** dashboard refreshes, **Then** latest batch timestamp shows within 1-2 seconds of actual generation

---

### Edge Cases

- What happens when emulated mode generates batches faster than the pipeline can process them (backpressure)?
- How does the system handle switching modes while generation is in progress?
- What happens if emulated batch size configuration is set to 0 or negative values?
- How does seed-based reproducibility work across mode switches?
- What happens when emulated mode runs for extended periods (hours) - does state accumulate correctly?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support a configuration flag to enable emulated fast-cadence generation mode
- **FR-002**: System MUST generate company onboarding batches every 5-10 seconds when in emulated mode
- **FR-003**: System MUST generate driver event batches every 5-10 seconds when in emulated mode
- **FR-004**: System MUST limit batch sizes to 5-20 records per batch in emulated mode
- **FR-005**: System MUST preserve all data schemas, quality injection rules, and generation logic between production and emulated modes
- **FR-006**: System MUST use the same seed-based reproducibility mechanism in emulated mode as production mode
- **FR-007**: System MUST emit batch metadata (batch ID, timestamp, record count, quality metrics) for every emulated batch
- **FR-008**: System MUST allow toggling between modes via configuration file without code changes
- **FR-009**: System MUST maintain separate interval configurations for company generation and driver event generation in emulated mode
- **FR-010**: System MUST log each emulated batch generation with timestamp, batch size, and processing duration
- **FR-011**: Emulated mode intervals MUST be configurable (defaulting to 5-10 seconds but adjustable)
- **FR-012**: Emulated mode batch sizes MUST be configurable (defaulting to 5-20 records but adjustable within reasonable bounds)

### Key Entities

- **Emulated Configuration**: Mode flag (production/emulated), company batch interval (seconds), driver batch interval (seconds), batch size limits (min/max records), quality injection settings
- **Batch Metadata**: Same structure as production but with higher frequency timestamps and smaller record counts
- **Generation Metrics**: Batch generation rate (batches/minute), record throughput (records/second), mode indicator, current interval setting

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can observe complete pipeline cycles (bronze → silver → gold) within 30 seconds when using emulated mode
- **SC-002**: Emulated batches are generated at 10-15 second intervals (configurable) with consistent timing variance under 1 second
- **SC-003**: Batch sizes in emulated mode remain between 5-20 records (configurable) per batch
- **SC-004**: Mode switching requires only configuration change, zero code modifications
- **SC-005**: Dashboard metrics update within 2 seconds of batch generation completion
- **SC-006**: Generated data in emulated mode passes identical validation rules as production mode (100% schema compatibility)
- **SC-007**: Developers can reproduce specific emulated sequences using the same seed values as production mode
- **SC-008**: Emulated mode can sustain continuous generation for at least 1 hour without performance degradation or state corruption

### Assumptions

- Existing quality injection framework (feature 005) will be reused without modification
- Existing Docker Compose infrastructure supports faster scheduling without resource constraints
- Dashboard refresh mechanism (if implemented) can handle sub-10-second update intervals
- Configuration validation will prevent invalid interval/size combinations (e.g., 0 seconds, negative batch sizes)
- Default emulated intervals set to 10 seconds (company) and 10 seconds (driver events) unless specified otherwise
- Default emulated batch sizes: 10 companies, 50 driver events per batch
