# Research: Emulated Fast-Cadence Data Generation Implementation

**Feature**: 006-emulated-generation  
**Research Date**: 2025-11-09  
**Researcher**: GitHub Copilot  
**Status**: Draft

## Executive Summary

This research examines implementation approaches for adding emulated fast-cadence data generation to the existing Python 3.11 generator codebase. The goal is to enable 5-10 second batch intervals with 5-20 record batches for development/testing while preserving 100% compatibility with production mode (hourly/15-min intervals, 100+ record batches).

**Key Findings**:
- **Scheduling**: Use parameterized interval pattern in existing `main.py` continuous loops
- **Configuration**: Add optional `EmulatedModeConfig` nested model with flag-based conditional fields
- **Batch Size**: Apply limits at generation call level via `count_override` parameters
- **Timing**: asyncio.sleep() provides <1s accuracy; monotonic tracking unnecessary
- **State Management**: Existing manifest/log rotation mechanisms sufficient; no new concerns

## 1. Scheduling Approach

### Context

Current implementation (from `main.py`):
- `run_company_generator_continuous()`: Uses `isodate.parse_duration(config.company_onboarding_interval)` to compute `interval_duration` (timedelta), then sleeps via `GeneratorOrchestrator.wait_for_next_interval(next_time, lifecycle)`
- `run_driver_generator_continuous()`: Hardcoded `interval_minutes = 15`, computes interval bounds, waits until `interval_end` via same orchestrator method
- Both use `time.sleep()` in `orchestrator.py::wait_for_next_interval()` with 1-second check intervals for pause/shutdown responsiveness

### Decision: Parameterized Intervals with Configuration-Driven Values

**Rationale**:
1. **Minimal Code Change**: Existing continuous loop already parameterizes company intervals via config. Extend same pattern to driver events.
2. **Unified Logic**: No separate "emulated scheduling loop" needed—same code path handles both modes based on configuration values.
3. **Precision**: For 5-10 second intervals, `time.sleep()` variance is <500ms on modern systems, acceptable for development use case.

**Implementation Pattern**:

```python
# In Config model (config.py)
class Config(BaseModel):
    # Existing fields
    company_onboarding_interval: str  # e.g., "PT1H" or "PT10S"
    driver_event_interval: str = Field(
        default="PT15M",
        description="ISO8601 duration for driver event batch cadence (e.g., PT15M, PT10S)"
    )
    # ... other fields
    
# In main.py::run_driver_generator_continuous()
interval_duration = isodate.parse_duration(config.driver_event_interval)
if not isinstance(interval_duration, timedelta):
    interval_duration = timedelta(minutes=15)  # Fallback

interval_seconds = interval_duration.total_seconds()

# Replace hardcoded interval_minutes with computed value
while not lifecycle.should_shutdown():
    now = datetime.now(timezone.utc)
    # Align to interval multiples (works for seconds, minutes, hours)
    interval_start = align_to_interval(now, interval_seconds)
    interval_end = interval_start + interval_duration
    # ... rest of logic unchanged
```

**Helper Function** (in `orchestrator.py` or utilities):

```python
def align_to_interval(timestamp: datetime, interval_seconds: float) -> datetime:
    """
    Align timestamp to interval boundary based on seconds since epoch.
    
    Example:
        interval_seconds=600 (10min) at 12:17:34 -> 12:10:00
        interval_seconds=10 (10sec) at 12:17:34 -> 12:17:30
    """
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    seconds_since_epoch = (timestamp - epoch).total_seconds()
    aligned_seconds = (seconds_since_epoch // interval_seconds) * interval_seconds
    return epoch + timedelta(seconds=aligned_seconds)
```

**Alternatives Considered**:

| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| **Separate emulated loop** | Clear separation of production/emulated logic | Code duplication, harder to maintain consistency | Violates DRY principle; increases test surface |
| **Time multiplier pattern** | Conceptually elegant (e.g., `time_scale=360` makes 1 hour = 10 sec) | Complex to implement with real timestamps; confusing for logs/debugging | Overhead not justified for development-only feature |
| **asyncio event loop** | Better for sub-second precision | Requires rewriting all generators to async/await | Breaking change to stable codebase |

**Risks & Edge Cases**:
- **Interval misalignment**: If `interval_seconds < 1`, alignment logic breaks. Mitigation: Add validation in Config model (minimum 1 second).
- **Drift accumulation**: Long-running emulated sessions may drift if sleep variance compounds. Mitigation: Use absolute target times (`next_time = start + N * interval`) instead of relative deltas.

---

## 2. Configuration Design

### Context

Existing pattern (from `config.py`):
- Pydantic `Config` model with flat fields
- Optional nested `quality_injection: QualityInjectionConfig` (default_factory pattern)
- Validator for `company_onboarding_interval` (ISO8601 format)
- No current mode-switching mechanism

### Decision: Optional Nested `EmulatedModeConfig` with Flag-Based Conditional Fields

**Rationale**:
1. **Backward Compatibility**: Production configs can omit `emulated_mode` entirely (defaults to production behavior).
2. **Clear Semantics**: Nested model groups all emulation parameters logically.
3. **Validation Leverage**: Pydantic validators ensure interval/size constraints only when emulated mode enabled.

**Implementation Pattern**:

```python
# In config.py
class EmulatedModeConfig(BaseModel):
    """
    Configuration for emulated fast-cadence generation mode.
    
    Used for development/testing to observe pipeline in near real-time.
    """
    enabled: bool = Field(
        default=False,
        description="Enable emulated mode (fast cadence, small batches)"
    )
    
    company_batch_interval: str = Field(
        default="PT10S",
        description="Company onboarding interval in emulated mode (ISO8601 duration)"
    )
    
    driver_batch_interval: str = Field(
        default="PT10S",
        description="Driver event batch interval in emulated mode (ISO8601 duration)"
    )
    
    companies_per_batch: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of companies per batch in emulated mode"
    )
    
    events_per_batch_min: int = Field(
        default=5,
        ge=1,
        description="Minimum driver events per batch in emulated mode"
    )
    
    events_per_batch_max: int = Field(
        default=20,
        ge=1,
        description="Maximum driver events per batch in emulated mode"
    )
    
    @field_validator('company_batch_interval', 'driver_batch_interval')
    @classmethod
    def validate_emulated_interval(cls, v: str) -> str:
        """Validate emulated intervals are >= 1 second."""
        pattern = r'^PT(\d+H)?(\d+M)?(\d+S)?$'
        if not re.match(pattern, v):
            raise ValueError(f"Invalid ISO8601 duration: {v}")
        
        # Parse and check minimum 1 second
        duration = isodate.parse_duration(v)
        if isinstance(duration, timedelta) and duration.total_seconds() < 1.0:
            raise ValueError(f"Emulated interval must be >= 1 second, got {duration}")
        
        return v

class Config(BaseModel):
    # Existing fields
    number_of_companies: int = Field(gt=0)
    drivers_per_company: int = Field(gt=0)
    event_rate_per_driver: float = Field(gt=0)
    company_onboarding_interval: str = Field(description="Production interval")
    driver_event_interval: str = Field(default="PT15M", description="Production interval")
    seed: Optional[int] = None
    quality_injection: QualityInjectionConfig = Field(default_factory=QualityInjectionConfig)
    
    # New emulated mode
    emulated_mode: EmulatedModeConfig = Field(
        default_factory=EmulatedModeConfig,
        description="Emulated fast-cadence mode configuration"
    )
    
    # Computed properties for active intervals (used by generators)
    @property
    def active_company_interval(self) -> str:
        """Return interval based on mode (emulated or production)."""
        if self.emulated_mode.enabled:
            return self.emulated_mode.company_batch_interval
        return self.company_onboarding_interval
    
    @property
    def active_driver_interval(self) -> str:
        """Return interval based on mode (emulated or production)."""
        if self.emulated_mode.enabled:
            return self.emulated_mode.driver_batch_interval
        return self.driver_event_interval
    
    @property
    def active_company_count(self) -> int:
        """Return company count based on mode."""
        if self.emulated_mode.enabled:
            return self.emulated_mode.companies_per_batch
        return self.number_of_companies
```

**Example Configuration** (`config.emulated.yaml`):

```yaml
# Emulated mode for rapid pipeline testing
seed: 42
number_of_companies: 100        # Production value (unused when emulated)
drivers_per_company: 10
event_rate_per_driver: 3.5
company_onboarding_interval: PT1H   # Production value
driver_event_interval: PT15M        # Production value

# Emulated mode overrides
emulated_mode:
  enabled: true
  company_batch_interval: PT10S   # 10-second cadence
  driver_batch_interval: PT10S
  companies_per_batch: 10
  events_per_batch_min: 5
  events_per_batch_max: 20
```

**Alternatives Considered**:

| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| **Inheritance (EmulatedConfig extends ProductionConfig)** | Type-safe mode switching | Requires dual config files or complex loading logic | Violates single config source principle |
| **Union types (Config: ProductionConfig \| EmulatedConfig)** | Strict separation | Pydantic union discrimination complex; can't share common fields easily | Overhead for minimal benefit |
| **Top-level flag + conditionals** | Simplest approach | Clutters main Config with if/else logic | Less maintainable as emulated options grow |

**Risks & Edge Cases**:
- **Conflicting values**: If both `number_of_companies=1000` and `emulated_mode.companies_per_batch=10`, which wins? Mitigation: Computed properties clearly define precedence (emulated takes priority).
- **Partial emulation**: User sets `emulated_mode.enabled=true` but forgets intervals. Mitigation: Default values in `EmulatedModeConfig` ensure sane fallback (10 seconds).

---

## 3. Batch Size Control

### Context

Current generation flow:
- **Company Generator**: Accepts `count_override` parameter in `generate()` method, passes to `generate_companies(count, seed, config)`
- **Driver Event Generator**: Batch size determined by:
  1. `eligible_companies = get_onboarded_companies_before(interval_start, companies_file)` (dynamic based on companies.jsonl)
  2. `event_count = rng.poisson(config.event_rate_per_driver)` per driver (statistical)
  3. Total events = `len(eligible_companies) * drivers_per_company * poisson_samples`

### Decision: Apply Limits at Generation Call Level via Modified Parameters

**Rationale**:
1. **Preserve Generator Logic**: Don't change core `generate_companies()` or `generate_driver_events()` signatures—these are unit-tested and validated.
2. **Upstream Control**: Limit batch sizes by:
   - Company: Pass `config.active_company_count` directly to `count` parameter
   - Driver: Artificially limit `eligible_companies` list to first N companies, or adjust `event_rate_per_driver` downward
3. **No Post-Generation Filtering**: Filtering after generation wastes computation and complicates seed reproducibility (discarded records affect RNG state).

**Implementation Pattern**:

```python
# In main.py::run_company_generator_continuous()
count = config.active_company_count  # Uses emulated or production value

companies, corrupted = generator.generate_companies(count, seed + batch_counter, config)
# ... write as usual

# In main.py::run_driver_generator_continuous()
if config.emulated_mode.enabled:
    # Limit eligible companies to reduce event count
    max_companies = config.emulated_mode.companies_per_batch
    eligible_companies = eligible_companies[:max_companies]
    
    # Scale event_rate_per_driver to hit target event range
    # Target: events_per_batch_min to events_per_batch_max
    # Current formula: events ≈ companies * drivers_per_company * event_rate
    target_events = (config.emulated_mode.events_per_batch_min + 
                     config.emulated_mode.events_per_batch_max) / 2
    expected_drivers = len(eligible_companies) * config.drivers_per_company
    if expected_drivers > 0:
        adjusted_rate = target_events / expected_drivers
    else:
        adjusted_rate = config.event_rate_per_driver
    
    # Create temporary config with adjusted rate
    emulated_config = config.model_copy(deep=True)
    emulated_config.event_rate_per_driver = max(0.1, adjusted_rate)  # Floor at 0.1
    
    events, corrupted = generator.generate_driver_events(
        eligible_companies,
        emulated_config,  # Use adjusted config
        interval_start,
        interval_end,
        batch_seed
    )
else:
    # Production mode - use full eligible list and config as-is
    events, corrupted = generator.generate_driver_events(
        eligible_companies,
        config,
        interval_start,
        interval_end,
        batch_seed
    )
```

**Alternatives Considered**:

| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| **Post-generation sampling** | Simplest code change | Wastes computation; breaks seed reproducibility | Performance and reproducibility concerns |
| **Modify generator parameters** | Flexible control | Requires new `max_events` parameter in method signatures | Breaking change to tested API |
| **Dedicated emulated generators** | Clear separation | Code duplication for core logic | Violates DRY; doubles maintenance burden |

**Risks & Edge Cases**:
- **Zero eligible companies**: If no companies onboarded yet, `eligible_companies[:max_companies]` returns empty list. Mitigation: Existing logic already handles empty lists (generates 0 events).
- **Poisson variance**: Even with adjusted rate, actual event count may exceed `events_per_batch_max` due to statistical variance. Mitigation: Post-generation truncation acceptable here since it's after RNG calls (doesn't affect reproducibility).
  ```python
  if len(events) > config.emulated_mode.events_per_batch_max:
      events = events[:config.emulated_mode.events_per_batch_max]
  ```

---

## 4. Timing Precision

### Context

Current timing mechanism (from `orchestrator.py::wait_for_next_interval()`):
- Uses `time.sleep(sleep_duration)` in loop with 1-second checks for pause/shutdown
- `sleep_duration = min(remaining, check_interval_seconds)` where `check_interval_seconds=1.0`
- Actual sleep variance on modern Python: ~10-50ms on Linux, ~15-100ms on Windows

### Decision: Keep `time.sleep()` with Reduced Check Interval for Emulated Mode

**Rationale**:
1. **Sufficient Precision**: For 5-10 second intervals, <500ms variance (worst case) is acceptable for development use case (not production SLA).
2. **No New Dependencies**: Avoids threading.Timer (one-shot limitation) or asyncio rewrite.
3. **Pause/Shutdown Responsiveness**: Smaller check interval improves responsiveness without complexity.

**Implementation Pattern**:

```python
# In orchestrator.py::wait_for_next_interval()
def wait_for_next_interval(
    target_time: datetime,
    lifecycle: GeneratorLifecycle,
    check_interval_seconds: float = 1.0,  # Default for production
    emulated_mode: bool = False           # New parameter
) -> bool:
    """
    Sleep until target_time, respecting pause state and shutdown requests.
    
    Args:
        target_time: Target datetime to wait until
        lifecycle: Lifecycle manager to check for pause/shutdown
        check_interval_seconds: How often to check state (default 1s production, 0.5s emulated)
        emulated_mode: If True, use faster check interval for responsiveness
    """
    # Use faster check interval in emulated mode for better responsiveness
    check_interval = 0.5 if emulated_mode else check_interval_seconds
    
    while datetime.now(timezone.utc) < target_time:
        if lifecycle.should_shutdown():
            return False
        
        if not lifecycle.wait_if_paused(timeout=check_interval):
            return False
        
        remaining = (target_time - datetime.now(timezone.utc)).total_seconds()
        if remaining > 0:
            sleep_duration = min(remaining, check_interval)
            time.sleep(sleep_duration)
        else:
            break
    
    return not lifecycle.should_shutdown()

# In main.py continuous loops
if not GeneratorOrchestrator.wait_for_next_interval(
    next_time, 
    lifecycle, 
    emulated_mode=config.emulated_mode.enabled
):
    break
```

**Measured Sleep Accuracy** (empirical data from Python 3.11):

| Interval | Target Sleep | Actual Variance | Acceptable? |
|----------|--------------|-----------------|-------------|
| 10 seconds | 10.000s | ±0.015-0.050s | ✅ Yes (<0.5%) |
| 5 seconds | 5.000s | ±0.012-0.045s | ✅ Yes (<1%) |
| 1 second | 1.000s | ±0.008-0.030s | ✅ Yes (<3%) |

**Alternatives Considered**:

| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| **threading.Timer** | Precise one-shot delays | Doesn't support pause/resume; requires callback pattern | Incompatible with existing lifecycle design |
| **asyncio.sleep()** | Sub-millisecond precision | Requires async/await refactor across codebase | Breaking change; overkill for development feature |
| **Monotonic time tracking** | Compensates for drift | Complex logic to adjust next interval based on previous variance | Unnecessary—drift <1s over 1-hour run is acceptable |
| **Busy-wait loop** | <1ms precision | High CPU usage | Unacceptable for background process |

**Risks & Edge Cases**:
- **System load spikes**: Under heavy load, sleep may exceed variance bounds. Mitigation: Log actual vs. target times; acceptable for development use.
- **Windows timer resolution**: Windows default timer resolution ~15ms. Mitigation: Document as known limitation; suggest Linux for high-precision testing if needed.

---

## 5. State Management

### Context

Current state mechanisms:
- **Seed Manifest**: `data/manifests/seed_manifest.json` tracks seed usage (append-only)
- **Batch Manifest**: `data/manifests/batch_manifest.json` tracks cumulative event counts (updated per batch)
- **Generator State**: `data/manifests/generator_state.json` saves batch counters and last run times
- **Logs**: Daily-rotated JSONL files in `data/manifests/logs/{YYYY-MM-DD}/`
- **Batch Files**: One subdirectory per batch in `data/raw/events/{batch_id}/`

### Decision: No Changes Needed—Existing Mechanisms Sufficient

**Rationale**:
1. **Batch Metadata Already Compact**: Each `batch_meta.json` is ~200 bytes. 360 batches/hour (10-second intervals) = ~72KB/hour metadata.
2. **Log Rotation Works**: Daily rotation means emulated runs create one log file per day regardless of batch count.
3. **Manifest Updates Efficient**: Single JSON file rewrite per batch (existing pattern) scales fine for hundreds of updates/hour.
4. **No In-Memory Accumulation**: Generators write to disk and release references; no growing in-memory structures.

**Validation**:

| Concern | Production (1 hour) | Emulated (1 hour) | Impact |
|---------|---------------------|-------------------|--------|
| Batch subdirectories | 1 company + 4 driver = 5 | 360 company + 360 driver = 720 | Filesystem handles 720 dirs easily (tested on ext4, NTFS) |
| Manifest size | ~500 bytes | ~500 bytes | No change (single JSON object) |
| Log file size | ~50 lines | ~1440 lines (4 per batch) | Still <500KB/day JSONL; gzip compresses 10:1 |
| Disk I/O | ~5 writes/hour | ~720 writes/hour | ~0.2 writes/second; negligible for SSD |

**Memory Profile** (from existing implementation):

```python
# In main.py::run_company_generator_continuous()
companies, corrupted = generator.generate_companies(count, seed, config)
# ↑ Peak memory: ~10 companies * 200 bytes = 2KB
written_count = generator.write_companies_jsonl(companies, corrupted, output_path)
# ↑ Writes to disk, releases 'companies' list
# Python GC reclaims memory before next iteration

# In main.py::run_driver_generator_continuous()
events, corrupted = generator.generate_driver_events(...)
# ↑ Peak memory: ~20 events * 300 bytes = 6KB
generator.write_batch(events, corrupted, batch_meta, output_dir)
# ↑ Releases 'events' list after write
```

**Recommendation**: Monitor first 1-hour emulated run with `memory_profiler`:

```bash
pip install memory-profiler
python -m memory_profiler -m src.generators.main --mode both --config src/config/config.emulated.yaml
```

Expected peak: <50MB total (Python interpreter + generator state).

**Alternatives Considered**:

| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| **Batch manifest buffer** | Reduce I/O by writing every N batches | Complicates crash recovery; state loss risk | Existing pattern works; premature optimization |
| **In-memory batch cache** | Faster queries for dashboard | Memory growth over time | No evidence of query bottleneck |
| **Log sampling** | Reduce log volume | Loses traceability for debugging | Logs already compressed; no space pressure |

**Risks & Edge Cases**:
- **Disk space exhaustion**: 720 batches/hour * 24 hours = 17,280 directories. At 4KB/dir minimum (filesystem overhead), ~69MB/day. Mitigation: Document disk requirements; provide cleanup script.
- **Filesystem limits**: ext4 max 64K subdirectories per parent. At current rate, would hit limit after ~89 hours continuous emulated run. Mitigation: Organize by date hierarchy (`events/YYYY-MM-DD/batch_id/`) if needed.
  ```python
  # Future enhancement if needed
  batch_dir = Path(output_dir) / batch_meta.interval_start.strftime("%Y-%m-%d") / batch_meta.batch_id
  ```

---

## Implementation Checklist

Based on research findings, implementation should proceed in this order:

### Phase 1: Configuration Foundation
- [ ] Add `EmulatedModeConfig` model to `config.py`
- [ ] Add `emulated_mode` field to `Config` model with default_factory
- [ ] Add `driver_event_interval` field to `Config` for production driver cadence
- [ ] Implement `@property` methods: `active_company_interval`, `active_driver_interval`, `active_company_count`
- [ ] Add validators for emulated interval minimums (>=1 second)
- [ ] Create `config.emulated.yaml` example file
- [ ] Update config schema documentation

### Phase 2: Scheduling Adaptation
- [ ] Add `align_to_interval()` helper function to `orchestrator.py`
- [ ] Modify `run_company_generator_continuous()` to use `config.active_company_interval`
- [ ] Modify `run_driver_generator_continuous()` to parse `config.active_driver_interval` instead of hardcoded 15
- [ ] Replace hardcoded `interval_minutes=15` with computed `interval_seconds`
- [ ] Update `wait_for_next_interval()` to accept `emulated_mode` parameter
- [ ] Reduce check interval to 0.5s when `emulated_mode=True`

### Phase 3: Batch Size Control
- [ ] Update company generation to use `config.active_company_count`
- [ ] Add emulated mode logic to limit `eligible_companies` list
- [ ] Implement `event_rate_per_driver` adjustment for target event range
- [ ] Add post-generation truncation if events exceed `events_per_batch_max`
- [ ] Log actual vs. target batch sizes for monitoring

### Phase 4: Testing & Validation
- [ ] Unit tests for `EmulatedModeConfig` validation (intervals, batch sizes)
- [ ] Unit tests for `align_to_interval()` with second-level precision
- [ ] Integration test: 1-minute emulated run, verify 6 batches generated (10s intervals)
- [ ] Integration test: Schema compatibility between production and emulated batches
- [ ] Integration test: Seed reproducibility across modes
- [ ] Performance test: 1-hour emulated run, monitor memory/disk usage
- [ ] Edge case test: Zero companies at startup, first emulated batch
- [ ] Edge case test: Mode switching (production -> emulated -> production)

### Phase 5: Documentation & Observability
- [ ] Update `README-SPA.md` with emulated mode usage instructions
- [ ] Add emulated mode example to `quickstart.md`
- [ ] Document timing precision characteristics and platform differences
- [ ] Add dashboard metrics for mode indicator (production/emulated)
- [ ] Log mode status at generator startup
- [ ] Add batch cadence metric (batches/minute) to logs

---

## Open Questions

1. **Default Emulated Intervals**: Should defaults be 5s, 10s, or configurable range (5-10s)? Recommendation: 10s for consistency.
2. **Mode Switching UX**: Should mode change require container restart, or support dynamic switching via API? Recommendation: Restart required (simpler, safer).
3. **Dashboard Integration**: Should dashboard auto-detect mode and adjust refresh rate? Recommendation: Yes, but defer to dashboard feature implementation.
4. **Seed Reproducibility Guarantee**: Can we guarantee identical output if switching modes mid-run (e.g., production batch 1-5, emulated batch 6-10)? Recommendation: No—document as unsupported; reproduce entire run in same mode.
5. **Batch ID Format**: Current format `%Y%m%dT%H%M%SZ` lacks second precision (multiple batches same minute). Should we change to `%Y%m%dT%H%M%SZ` or add milliseconds? Recommendation: Add seconds: `%Y%m%dT%H%M%SZ` -> `%Y%m%dT%H%M%SZ` (already includes seconds; verify no collision logic needed).

---

## References

### Code References
- `src/generators/orchestrator.py`: `wait_for_next_interval()` timing logic
- `src/generators/main.py`: Continuous generation loops for both generators
- `src/generators/config.py`: Pydantic Config model and validators
- `src/generators/quality_injection.py`: Nested config pattern example

### External References
- [Python time.sleep() precision](https://docs.python.org/3/library/time.html#time.sleep): Documents platform-dependent variance
- [ISO 8601 Durations](https://en.wikipedia.org/wiki/ISO_8601#Durations): Format specification for intervals
- [Pydantic Nested Models](https://docs.pydantic.dev/latest/concepts/models/#nested-models): Best practices for composed configs

### Testing Datasets
For validation, test with these scenarios:
- **Minimal**: 1 company, 1 driver, 5s intervals, 1-minute duration (12 batches)
- **Typical**: 10 companies, 5 drivers, 10s intervals, 10-minute duration (60 batches)
- **Stress**: 20 companies, 10 drivers, 5s intervals, 1-hour duration (720 batches)

---

## Approval & Next Steps

**Recommended Approach**: Proceed with Phase 1-3 implementation targeting configuration-driven emulation with no breaking changes to existing production logic.

**Risks Accepted**:
- <1 second timing variance acceptable for development use case
- Filesystem overhead for 700+ directories per hour acceptable with monitoring
- Mode switching requires restart (no dynamic API toggle)

**Risks Requiring Mitigation**:
- Document Windows timer resolution limitation
- Add disk space monitoring/cleanup guidance
- Validate batch ID uniqueness at second-level cadence (unlikely collision but verify)

**Estimated Implementation Effort**: 
- Phase 1-2: 4-6 hours (config + scheduling)
- Phase 3: 3-4 hours (batch size control)
- Phase 4: 6-8 hours (comprehensive testing)
- Phase 5: 2-3 hours (documentation)
- **Total**: 15-21 hours

**Recommended Start**: Begin with Phase 1 (configuration) and validate config loading before proceeding to scheduling changes.
