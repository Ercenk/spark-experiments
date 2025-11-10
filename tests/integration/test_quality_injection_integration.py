"""Integration test for data quality injection feature."""

import json
import tempfile
from pathlib import Path
import shutil

from src.generators.company_generator import CompanyGenerator
from src.generators.driver_event_generator import DriverEventGenerator
from src.generators.config import Config
from src.generators.quality_injection import QualityInjectionConfig


def test_end_to_end_quality_injection_with_generators():
    """
    End-to-end test: Generate data with quality issues and verify they appear in output files.
    
    This test:
    1. Creates a config with quality injection enabled (50% error rate for high visibility)
    2. Generates companies and driver events
    3. Parses the output JSON files
    4. Verifies that corrupted records are actually written to bronze dataset
    5. Verifies that some records have expected quality issues (missing fields, nulls, malformed timestamps)
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        companies_file = Path(tmpdir) / "companies.jsonl"
        events_dir = Path(tmpdir) / "events"
        
        # Configuration with HIGH error rate for testing (50%)
        config = Config(
            number_of_companies=20,  # Increased to get more samples
            drivers_per_company=5,
            event_rate_per_driver=3.0,
            company_onboarding_interval="PT30M",
            seed=42,
            quality_injection=QualityInjectionConfig(
                enabled=True,
                error_rate=0.5,  # 50% of records will have issues
                missing_field_probability=0.4,
                null_value_probability=0.4,
                malformed_timestamp_probability=0.3,
                invalid_enum_probability=0.3,
                inject_in_driver_events=True,
                inject_in_companies=True,
                log_injected_issues=False  # Don't spam logs in test
            )
        )
        
        # Generate companies
        company_gen = CompanyGenerator()
        companies, corrupted_companies = company_gen.generate_companies(
            count=20,
            seed=42,
            config=config
        )
        
        # With 50% error rate, we should have BOTH valid and corrupted companies
        assert len(companies) > 0, "Should generate at least some valid companies"
        assert len(corrupted_companies) > 0, f"Should generate corrupted companies with 50% error rate, got {len(corrupted_companies)}"
        
        # Write companies (both valid and corrupted)
        written_count = company_gen.write_companies_jsonl(companies, corrupted_companies, str(companies_file))
        assert companies_file.exists()
        assert written_count == len(companies) + len(corrupted_companies), "Should write all records"
        
        # Read and check company records from file
        company_records = []
        with open(companies_file, 'r') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    company_records.append(record)
        
        assert len(company_records) == written_count, "All written records should be readable as JSON"
        
        # Check that some records have quality issues
        records_with_nulls = sum(1 for r in company_records if any(v is None for v in r.values()))
        records_missing_fields = sum(1 for r in company_records if 'company_id' not in r or 'geography' not in r)
        
        # With 50% error rate and high probabilities, we should see quality issues
        assert records_with_nulls > 0 or records_missing_fields > 0, \
            f"Should have records with quality issues. Nulls: {records_with_nulls}, Missing fields: {records_missing_fields}"
        
        # Generate driver events
        from datetime import datetime, timezone, timedelta
        
        interval_start = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        interval_end = interval_start + timedelta(minutes=15)
        
        event_gen = DriverEventGenerator()
        
        # Get company IDs for coordination (only from valid companies that have company_id)
        company_ids = [c.company_id for c in companies]
        
        events, corrupted_events = event_gen.generate_driver_events(
            companies=company_ids,
            config=config,
            interval_start=interval_start,
            interval_end=interval_end,
            seed=42
        )
        
        # Should generate both valid and corrupted events
        assert len(events) > 0, "Should generate at least some valid events"
        assert len(corrupted_events) > 0, f"Should generate corrupted events with 50% error rate, got {len(corrupted_events)}"
        
        print(f"Generated {len(events)} valid events and {len(corrupted_events)} corrupted events")


def test_quality_injection_disabled_produces_clean_data():
    """
    Verify that with quality injection disabled, all records are valid.
    """
    config = Config(
        number_of_companies=5,
        drivers_per_company=3,
        event_rate_per_driver=2.0,
        company_onboarding_interval="PT30M",
        seed=42,
        quality_injection=QualityInjectionConfig(enabled=False)
    )
    
    # Generate companies
    company_gen = CompanyGenerator()
    companies, corrupted_companies = company_gen.generate_companies(count=5, seed=42, config=config)
    
    # All should be valid, none corrupted
    assert len(companies) == 5, "Should generate exactly 5 companies when injection disabled"
    assert len(corrupted_companies) == 0, "Should have zero corrupted companies when injection disabled"
    
    for company in companies:
        # All required fields should be present
        company_dict = company.model_dump()
        assert 'company_id' in company_dict
        assert 'geography' in company_dict
        assert 'active' in company_dict
        assert 'created_at' in company_dict
        
        # No nulls
        assert company_dict['company_id'] is not None
        assert company_dict['geography'] is not None
        assert company_dict['active'] is not None
        assert company_dict['created_at'] is not None


def test_bronze_dataset_contains_corrupted_records():
    """
    Critical test: Verify that corrupted records are actually written to bronze JSONL files
    and can be parsed to verify quality issues are present in the data.
    
    This test validates the core use case: injecting realistic errors into bronze data
    so the medallion pipeline can test its validation and cleansing logic.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        companies_file = Path(tmpdir) / "companies.jsonl"
        events_dir = Path(tmpdir) / "events"
        events_dir.mkdir(parents=True, exist_ok=True)
        
        # High error rate config for guaranteed quality issues
        config = Config(
            number_of_companies=30,
            drivers_per_company=5,
            event_rate_per_driver=4.0,
            company_onboarding_interval="PT30M",
            seed=99,  # Different seed for variety
            quality_injection=QualityInjectionConfig(
                enabled=True,
                error_rate=0.6,  # 60% error rate
                missing_field_probability=0.5,
                null_value_probability=0.5,
                malformed_timestamp_probability=0.5,
                invalid_enum_probability=0.5,
                inject_in_driver_events=True,
                inject_in_companies=True,
                log_injected_issues=False
            )
        )
        
        # Generate and write companies
        company_gen = CompanyGenerator()
        companies, corrupted_companies = company_gen.generate_companies(count=30, seed=99, config=config)
        written_count = company_gen.write_companies_jsonl(companies, corrupted_companies, str(companies_file))
        
        # Verify companies were written
        assert written_count > 0
        assert len(corrupted_companies) > 0, "Should have corrupted companies with 60% error rate"
        
        # Read bronze companies file and analyze
        company_records = []
        with open(companies_file, 'r') as f:
            for line in f:
                if line.strip():
                    company_records.append(json.loads(line))
        
        assert len(company_records) == written_count
        
        # Analyze quality issues in written data
        companies_with_nulls = 0
        companies_missing_company_id = 0
        companies_missing_geography = 0
        companies_with_malformed_timestamp = 0
        
        for record in company_records:
            has_null = any(v is None for v in record.values())
            if has_null:
                companies_with_nulls += 1
            
            if 'company_id' not in record:
                companies_missing_company_id += 1
            
            if 'geography' not in record:
                companies_missing_geography += 1
            
            if 'created_at' in record:
                timestamp = record['created_at']
                # Check for malformed timestamp patterns
                if not isinstance(timestamp, str) or \
                   ('13' in timestamp and 'T' in timestamp) or \
                   ('32' in timestamp) or \
                   ('25:' in timestamp):
                    companies_with_malformed_timestamp += 1
        
        # With 60% error rate, we should see quality issues
        total_quality_issues = (companies_with_nulls + companies_missing_company_id + 
                               companies_missing_geography + companies_with_malformed_timestamp)
        
        assert total_quality_issues > 0, \
            f"Bronze dataset should contain quality issues. Found: nulls={companies_with_nulls}, " \
            f"missing_id={companies_missing_company_id}, missing_geo={companies_missing_geography}, " \
            f"malformed_ts={companies_with_malformed_timestamp}"
        
        print(f"✓ Companies: {len(company_records)} total, {total_quality_issues} with quality issues")
        
        # Generate and write driver events
        from datetime import datetime, timezone, timedelta
        from src.generators.driver_event_generator import DriverEventGenerator
        
        interval_start = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        interval_end = interval_start + timedelta(minutes=15)
        
        event_gen = DriverEventGenerator()
        company_ids = [c.company_id for c in companies]
        
        events, corrupted_events = event_gen.generate_driver_events(
            companies=company_ids,
            config=config,
            interval_start=interval_start,
            interval_end=interval_end,
            seed=99
        )
        
        assert len(corrupted_events) > 0, "Should have corrupted events with 60% error rate"
        
        # Write events using the generator's write_batch method
        from src.generators.models import DriverEventBatch
        batch_meta = DriverEventBatch(
            batch_id="20240101T120000Z",
            interval_start=interval_start,
            interval_end=interval_end,
            event_count=len(events),
            seed=99
        )
        
        event_gen.write_batch(events, corrupted_events, batch_meta, str(events_dir))
        
        # Read bronze events file
        events_file = events_dir / "20240101T120000Z" / "events.jsonl"
        assert events_file.exists(), "Events file should be created"
        
        event_records = []
        with open(events_file, 'r') as f:
            for line in f:
                if line.strip():
                    event_records.append(json.loads(line))
        
        assert len(event_records) == len(events) + len(corrupted_events), \
            "Should write all events (valid + corrupted)"
        
        # Analyze event quality issues
        events_with_nulls = 0
        events_missing_driver_id = 0
        events_missing_event_type = 0
        events_with_invalid_event_type = 0
        events_with_malformed_timestamp = 0
        
        VALID_EVENT_TYPES = ["start driving", "stopped driving", "delivered"]
        
        for record in event_records:
            if any(v is None for v in record.values()):
                events_with_nulls += 1
            
            if 'driver_id' not in record:
                events_missing_driver_id += 1
            
            if 'event_type' not in record:
                events_missing_event_type += 1
            elif record['event_type'] not in VALID_EVENT_TYPES:
                events_with_invalid_event_type += 1
            
            if 'timestamp' in record:
                ts = record['timestamp']
                if not isinstance(ts, str) or \
                   ('13' in ts and 'T' in ts) or \
                   ('32' in ts) or \
                   ('25:' in ts) or \
                   'not-a-timestamp' in ts:
                    events_with_malformed_timestamp += 1
        
        total_event_issues = (events_with_nulls + events_missing_driver_id + 
                             events_missing_event_type + events_with_invalid_event_type + 
                             events_with_malformed_timestamp)
        
        assert total_event_issues > 0, \
            f"Bronze events should contain quality issues. Found: nulls={events_with_nulls}, " \
            f"missing_driver_id={events_missing_driver_id}, missing_event_type={events_missing_event_type}, " \
            f"invalid_event_type={events_with_invalid_event_type}, malformed_ts={events_with_malformed_timestamp}"
        
        print(f"✓ Events: {len(event_records)} total, {total_event_issues} with quality issues")
        print(f"  - Nulls: {events_with_nulls}")
        print(f"  - Missing driver_id: {events_missing_driver_id}")
        print(f"  - Missing event_type: {events_missing_event_type}")
        print(f"  - Invalid event_type: {events_with_invalid_event_type}")
        print(f"  - Malformed timestamp: {events_with_malformed_timestamp}")


if __name__ == '__main__':
    # Can run directly for debugging
    test_end_to_end_quality_injection_with_generators()
    test_quality_injection_disabled_produces_clean_data()
    test_bronze_dataset_contains_corrupted_records()
    print("✓ All integration tests passed")
