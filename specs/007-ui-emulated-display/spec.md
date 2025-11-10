# Feature Specification: UI Refinements for Emulated Mode Display

**Feature Branch**: `007-ui-emulated-display`  
**Created**: 2025-11-09  
**Status**: Draft  
**Input**: User description: "refine UI for presenting emulated data generation output"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Mode Visibility at a Glance (Priority: P1)

As a pipeline developer working with emulated mode, I want to immediately see which generation mode is active when I open the dashboard, so I don't mistake fast-cadence test data for production data.

**Why this priority**: Critical safety feature - prevents confusion between test and production modes. Without clear mode indication, developers might misinterpret batch metrics or make incorrect assumptions about data volume.

**Independent Test**: Open dashboard while generator runs in emulated mode. Mode indicator should be visible within 2 seconds without scrolling. Switch to production mode config and restart - indicator should update to reflect production mode.

**Acceptance Scenarios**:

1. **Given** generator running in emulated mode, **When** user opens dashboard, **Then** a prominent badge/indicator displays "Emulated Mode" near the top of the interface
2. **Given** generator running in production mode, **When** user opens dashboard, **Then** the mode indicator displays "Production Mode" or is visibly absent/different styling
3. **Given** user switches between tabs/windows, **When** returning to dashboard, **Then** mode indicator remains visible and current

---

### User Story 2 - Emulated Configuration Details on Demand (Priority: P2)

As a pipeline developer, I want to see the active emulated mode configuration parameters (intervals, batch sizes) when in emulated mode, so I can verify my test setup without opening config files.

**Why this priority**: Enhances developer efficiency - reduces context switching between UI and config files. Particularly valuable when troubleshooting timing or batch size issues.

**Independent Test**: Start generator with emulated config (10s intervals, 10 companies, 5-20 events). Open dashboard and view configuration details. Values should match the active config file.

**Acceptance Scenarios**:

1. **Given** emulated mode active, **When** user views health panel, **Then** configuration details show company interval (seconds), driver interval (seconds), companies per batch, and event range
2. **Given** production mode active, **When** user views health panel, **Then** emulated configuration details are hidden/not displayed
3. **Given** multiple emulated config presets available, **When** user switches between them and restarts, **Then** displayed values update to match active config

---

### User Story 3 - Enhanced Batch Metrics for Fast Cadence (Priority: P2)

As a pipeline developer observing emulated mode, I want batch count metrics to refresh more frequently and display cadence indicators, so I can verify the 5-10 second generation intervals are working correctly.

**Why this priority**: Core value proposition of emulated mode is observing fast cadence. Current 5-second polling may be adequate, but batch/minute metrics would better demonstrate the speed difference vs production.

**Independent Test**: Run emulated mode for 2 minutes. Dashboard should show 12-24 company batches (at 10s intervals) and display a cadence metric indicating batches per minute (approximately 6/min).

**Acceptance Scenarios**:

1. **Given** emulated mode running for 1 minute, **When** viewing health metrics, **Then** batch counts increase visibly every 10 seconds during polling
2. **Given** emulated mode active, **When** viewing generator statistics, **Then** a "batches per minute" or "cadence" metric is displayed for both company and driver generators
3. **Given** switching from production to emulated mode, **When** observing metrics over 1 minute, **Then** batch count growth rate is visibly faster (6/min vs 1/hour for companies)

---

### User Story 4 - Log Message Mode Context (Priority: P3)

As a pipeline developer reviewing logs, I want log messages to indicate when they're from emulated mode batches, so I can quickly filter or identify test-related entries.

**Why this priority**: Nice-to-have enhancement - helps when reviewing historical logs after multiple test runs. Lower priority because mode is already visible in health panel.

**Independent Test**: Generate 5 batches in emulated mode. Open logs panel and verify batch generation messages include mode context (e.g., "generated batch 3 (emulated mode)").

**Acceptance Scenarios**:

1. **Given** emulated mode running, **When** viewing log entries, **Then** batch generation messages include "(emulated mode)" or similar indicator in the message text
2. **Given** production mode running, **When** viewing log entries, **Then** batch messages either omit mode indicator or show "(production mode)"
3. **Given** mixed mode logs from multiple test sessions, **When** reading chronologically, **Then** mode transitions are clearly visible in log messages

---

### Edge Cases

- What happens when API returns `generation_mode` field as null or undefined (older backend version)?
- How does UI handle emulated_config field missing when mode="emulated" (API contract violation)?
- What happens during mode transitions when config changes but generator hasn't restarted yet?
- How does UI display very long uptimes in emulated mode (hours of fast batches = thousands of batch count)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Dashboard MUST display generation mode indicator prominently when health data is available
- **FR-002**: Dashboard MUST differentiate visually between "production" and "emulated" modes using color, text, or iconography
- **FR-003**: Dashboard MUST show emulated configuration details (intervals in seconds, batch sizes, event ranges) when mode is "emulated"
- **FR-004**: Dashboard MUST hide emulated configuration section when mode is "production" or emulated_config is absent
- **FR-005**: Health polling MUST parse and handle new API fields: `generation_mode` (string) and `emulated_config` (object)
- **FR-006**: Dashboard MUST calculate and display batch cadence metrics (batches per minute) for both generators when data is available
- **FR-007**: Dashboard MUST handle missing or null `generation_mode` field gracefully (assume production mode as fallback)
- **FR-008**: Log entries MUST display mode context from log message text when present (no new parsing required - already in backend messages)
- **FR-009**: Mode indicator MUST update within one polling cycle (5 seconds) when backend mode changes
- **FR-010**: Dashboard MUST maintain accessibility standards (WCAG 2.1 AA) for mode indicators using color + text/icon combinations

### Key Entities

- **Generation Mode**: Enum representing current generator operation mode (production, emulated)
- **Emulated Configuration**: Settings active during emulated mode (company interval, driver interval, companies per batch, events per batch range)
- **Batch Cadence Metric**: Calculated rate of batch generation (batches per minute) derived from total_batches and uptime

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can identify active generation mode within 2 seconds of opening dashboard
- **SC-002**: Mode indicator is visible in viewport without scrolling on standard desktop resolutions (1920x1080 and above)
- **SC-003**: Emulated configuration details display all 4 parameters (company interval, driver interval, batch size, event range) when mode is emulated
- **SC-004**: Dashboard correctly handles mode field absence by defaulting to production mode without errors or warnings
- **SC-005**: Batch cadence metrics update every 5 seconds (following existing polling interval) and accurately reflect batches per minute
- **SC-006**: 100% of log messages generated in emulated mode include mode context indicator (verified by backend implementation in feature 006)
- **SC-007**: Mode indicator passes WCAG 2.1 AA contrast requirements and includes non-color visual differentiation (icon or text)

## Assumptions

- Backend API changes from feature 006 are deployed and available (generation_mode and emulated_config fields)
- Existing 5-second polling interval for health data is sufficient for observing emulated mode cadence
- Log message format already includes mode context from backend (no frontend parsing changes needed)
- Dashboard UI follows existing Fluent UI design system and token structure
- Mode switching requires generator restart (not a runtime toggle) - UI only needs to reflect current state
- Standard batch cadence calculation: (total_batches / uptime_minutes) = batches per minute

## Out of Scope

- Real-time WebSocket updates (maintaining existing 5-second HTTP polling)
- Historical mode switching visualization (timeline of production vs emulated periods)
- Configuration file editing from UI (mode changes still require config file updates)
- Batch size distribution charts or histograms (future enhancement)
- Automatic mode detection/recommendation based on development environment
- A/B testing between production and emulated mode within same session
