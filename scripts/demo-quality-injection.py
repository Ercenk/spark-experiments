#!/usr/bin/env python
"""
Demonstration script for data quality injection feature.

Shows how to generate bronze data with configurable quality issues
for testing data pipeline validation and cleansing logic.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generators.company_generator import CompanyGenerator
from src.generators.driver_event_generator import DriverEventGenerator
from src.generators.config import Config
from src.generators.quality_injection import QualityInjectionConfig
from src.generators.models import DriverEventBatch


def demonstrate_quality_injection():
    """
    Demonstrate quality injection with actual data generation.
    """
    print("=" * 80)
    print("DATA QUALITY INJECTION DEMONSTRATION")
    print("=" * 80)
    print()
    
    # Create output directories
    output_dir = Path("demo_output")
    output_dir.mkdir(exist_ok=True)
    companies_file = output_dir / "companies.jsonl"
    events_dir = output_dir / "events"
    events_dir.mkdir(exist_ok=True)
    
    # Configuration with quality injection enabled
    config = Config(
        number_of_companies=10,
        drivers_per_company=3,
        event_rate_per_driver=5.0,
        company_onboarding_interval="PT30M",
        seed=42,
        quality_injection=QualityInjectionConfig(
            enabled=True,
            error_rate=0.3,  # 30% of records will have issues
            missing_field_probability=0.4,
            null_value_probability=0.4,
            malformed_timestamp_probability=0.3,
            invalid_enum_probability=0.3,
            inject_in_driver_events=True,
            inject_in_companies=True,
            log_injected_issues=False
        )
    )
    
    print(f"Configuration:")
    print(f"  - Number of companies: {config.number_of_companies}")
    print(f"  - Drivers per company: {config.drivers_per_company}")
    print(f"  - Quality injection enabled: {config.quality_injection.enabled}")
    print(f"  - Error rate: {config.quality_injection.error_rate * 100}%")
    print()
    
    # Generate companies
    print("Generating companies...")
    company_gen = CompanyGenerator()
    companies, corrupted_companies = company_gen.generate_companies(
        count=config.number_of_companies,
        seed=42,
        config=config
    )
    
    print(f"  ✓ Generated {len(companies)} valid companies")
    print(f"  ✓ Generated {len(corrupted_companies)} corrupted companies")
    
    # Write companies
    written_count = company_gen.write_companies_jsonl(
        companies, 
        corrupted_companies, 
        str(companies_file)
    )
    print(f"  ✓ Wrote {written_count} total companies to {companies_file}")
    print()
    
    # Analyze company data
    print("Analyzing company quality issues...")
    company_records = []
    with open(companies_file, 'r') as f:
        for line in f:
            if line.strip():
                company_records.append(json.loads(line))
    
    companies_with_issues = 0
    issue_types = {
        'missing_company_id': 0,
        'missing_geography': 0,
        'null_values': 0,
        'malformed_timestamp': 0
    }
    
    for record in company_records:
        has_issue = False
        
        if 'company_id' not in record:
            issue_types['missing_company_id'] += 1
            has_issue = True
        
        if 'geography' not in record:
            issue_types['missing_geography'] += 1
            has_issue = True
        
        if any(v is None for v in record.values()):
            issue_types['null_values'] += 1
            has_issue = True
        
        if 'created_at' in record:
            ts = record['created_at']
            if '13' in str(ts) or '25:' in str(ts):
                issue_types['malformed_timestamp'] += 1
                has_issue = True
        
        if has_issue:
            companies_with_issues += 1
    
    print(f"  Total companies: {len(company_records)}")
    print(f"  Companies with quality issues: {companies_with_issues}")
    for issue_type, count in issue_types.items():
        if count > 0:
            print(f"    - {issue_type}: {count}")
    print()
    
    # Generate driver events
    print("Generating driver events...")
    interval_start = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    interval_end = interval_start + timedelta(minutes=15)
    
    event_gen = DriverEventGenerator()
    company_ids = [c.company_id for c in companies]
    
    events, corrupted_events = event_gen.generate_driver_events(
        companies=company_ids,
        config=config,
        interval_start=interval_start,
        interval_end=interval_end,
        seed=42
    )
    
    print(f"  ✓ Generated {len(events)} valid events")
    print(f"  ✓ Generated {len(corrupted_events)} corrupted events")
    
    # Write events
    batch_meta = DriverEventBatch(
        batch_id="20240101T120000Z",
        interval_start=interval_start,
        interval_end=interval_end,
        event_count=len(events),
        seed=42
    )
    
    event_gen.write_batch(events, corrupted_events, batch_meta, str(events_dir))
    events_file = events_dir / "20240101T120000Z" / "events.jsonl"
    print(f"  ✓ Wrote {len(events) + len(corrupted_events)} total events to {events_file}")
    print()
    
    # Analyze event data
    print("Analyzing event quality issues...")
    event_records = []
    with open(events_file, 'r') as f:
        for line in f:
            if line.strip():
                event_records.append(json.loads(line))
    
    events_with_issues = 0
    event_issue_types = {
        'missing_driver_id': 0,
        'missing_event_type': 0,
        'invalid_event_type': 0,
        'null_values': 0,
        'malformed_timestamp': 0
    }
    
    VALID_EVENT_TYPES = ["start driving", "stopped driving", "delivered"]
    
    for record in event_records:
        has_issue = False
        
        if 'driver_id' not in record:
            event_issue_types['missing_driver_id'] += 1
            has_issue = True
        
        if 'event_type' not in record:
            event_issue_types['missing_event_type'] += 1
            has_issue = True
        elif record['event_type'] not in VALID_EVENT_TYPES:
            event_issue_types['invalid_event_type'] += 1
            has_issue = True
        
        if any(v is None for v in record.values()):
            event_issue_types['null_values'] += 1
            has_issue = True
        
        if 'timestamp' in record:
            ts = record['timestamp']
            if '13' in str(ts) or '25:' in str(ts) or 'not-a-timestamp' in str(ts):
                event_issue_types['malformed_timestamp'] += 1
                has_issue = True
        
        if has_issue:
            events_with_issues += 1
    
    print(f"  Total events: {len(event_records)}")
    print(f"  Events with quality issues: {events_with_issues}")
    for issue_type, count in event_issue_types.items():
        if count > 0:
            print(f"    - {issue_type}: {count}")
    print()
    
    # Show sample records
    print("Sample records from bronze dataset:")
    print()
    print("Valid company:")
    valid_company = next((r for r in company_records if 'company_id' in r and all(v is not None for v in r.values())), None)
    if valid_company:
        print(f"  {json.dumps(valid_company, indent=2)}")
    print()
    
    print("Corrupted company (example):")
    corrupted_company = next((r for r in company_records 
                             if 'company_id' not in r or any(v is None for v in r.values())), None)
    if corrupted_company:
        print(f"  {json.dumps(corrupted_company, indent=2)}")
        issues = []
        if 'company_id' not in corrupted_company:
            issues.append("missing company_id")
        if any(v is None for v in corrupted_company.values()):
            issues.append("contains null values")
        print(f"  Issues: {', '.join(issues)}")
    print()
    
    print("Valid event:")
    valid_event = next((r for r in event_records 
                       if 'driver_id' in r and 'event_type' in r and r.get('event_type') in VALID_EVENT_TYPES), None)
    if valid_event:
        print(f"  {json.dumps(valid_event, indent=2)}")
    print()
    
    print("Corrupted event (example):")
    corrupted_event = next((r for r in event_records 
                           if 'driver_id' not in r or r.get('event_type') not in VALID_EVENT_TYPES or any(v is None for v in r.values())), None)
    if corrupted_event:
        print(f"  {json.dumps(corrupted_event, indent=2)}")
        issues = []
        if 'driver_id' not in corrupted_event:
            issues.append("missing driver_id")
        if 'event_type' not in corrupted_event:
            issues.append("missing event_type")
        elif corrupted_event.get('event_type') not in VALID_EVENT_TYPES:
            issues.append(f"invalid event_type: {corrupted_event['event_type']}")
        if any(v is None for v in corrupted_event.values()):
            issues.append("contains null values")
        print(f"  Issues: {', '.join(issues)}")
    print()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Bronze dataset created in: {output_dir}")
    print(f"  - Companies: {companies_file} ({len(company_records)} records)")
    print(f"  - Events: {events_file} ({len(event_records)} records)")
    print()
    print(f"Quality metrics:")
    print(f"  - Company error rate: {companies_with_issues / len(company_records) * 100:.1f}%")
    print(f"  - Event error rate: {events_with_issues / len(event_records) * 100:.1f}%")
    print()
    print("Next steps:")
    print("  1. Use this bronze data to test medallion pipeline validation")
    print("  2. Verify pipeline correctly flags/cleanses quality issues")
    print("  3. Measure data quality metrics in Silver layer")
    print()


if __name__ == '__main__':
    demonstrate_quality_injection()
