"""
Data quality injector for introducing realistic quality issues into generated records.

Supports configurable injection of missing fields, nulls, malformed values, duplicates, etc.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import numpy as np
from .quality_injection import QualityInjectionConfig, InjectedIssue

logger = logging.getLogger(__name__)


class QualityInjector:
    """
    Injects configurable data quality issues into generated records.
    
    Uses seeded random number generation for reproducibility.
    Logs all injected issues for traceability.
    """
    
    def __init__(self, config: QualityInjectionConfig, rng: np.random.RandomState):
        """
        Initialize quality injector.
        
        Args:
            config: Quality injection configuration
            rng: NumPy RandomState instance (shared with generator for reproducibility)
        """
        self.config = config
        self.rng = rng
        self.issues_log: List[InjectedIssue] = []
        
    def should_inject_error(self) -> bool:
        """Determine if this record should have quality issues injected."""
        if not self.config.enabled:
            return False
        return self.rng.random() < self.config.error_rate
    
    def inject_into_driver_event(self, event: Dict[str, Any], driver_id: str) -> Dict[str, Any]:
        """
        Inject quality issues into a driver event record.
        
        Args:
            event: Original event dictionary
            driver_id: Driver identifier for logging
            
        Returns:
            Modified event dictionary (may have issues injected)
        """
        if not self.config.enabled or not self.config.inject_in_driver_events:
            return event
        
        if not self.should_inject_error():
            return event
        
        # Make a copy to avoid modifying original
        corrupted = event.copy()
        record_id = f"driver_event_{driver_id}_{event.get('timestamp', 'unknown')}"
        
        # Randomly choose which issue type(s) to inject
        if self.rng.random() < self.config.missing_field_probability:
            corrupted = self._inject_missing_field(corrupted, record_id, ["event_type", "driver_id"])
        
        if self.rng.random() < self.config.null_value_probability:
            corrupted = self._inject_null_value(corrupted, record_id, ["event_type", "driver_id", "timestamp"])
        
        if self.rng.random() < self.config.malformed_timestamp_probability:
            corrupted = self._inject_malformed_timestamp(corrupted, record_id, "timestamp")
        
        if self.rng.random() < self.config.invalid_enum_probability:
            corrupted = self._inject_invalid_enum(corrupted, record_id, "event_type")
        
        if self.rng.random() < self.config.extra_field_probability:
            corrupted = self._inject_extra_field(corrupted, record_id)
        
        if self.rng.random() < self.config.boundary_violation_probability:
            corrupted = self._inject_boundary_violation(corrupted, record_id, "timestamp")
        
        return corrupted
    
    def inject_into_company(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inject quality issues into a company record.
        
        Args:
            company: Original company dictionary
            
        Returns:
            Modified company dictionary (may have issues injected)
        """
        if not self.config.enabled or not self.config.inject_in_companies:
            return company
        
        if not self.should_inject_error():
            return company
        
        # Make a copy to avoid modifying original
        corrupted = company.copy()
        record_id = f"company_{company.get('company_id', 'unknown')}"
        
        # Randomly choose which issue type(s) to inject
        # Company fields: company_id, geography, active, created_at
        if self.rng.random() < self.config.missing_field_probability:
            corrupted = self._inject_missing_field(corrupted, record_id, ["geography", "active", "company_id"])
        
        if self.rng.random() < self.config.null_value_probability:
            corrupted = self._inject_null_value(corrupted, record_id, ["geography", "active", "company_id", "created_at"])
        
        if self.rng.random() < self.config.malformed_timestamp_probability:
            corrupted = self._inject_malformed_timestamp(corrupted, record_id, "created_at")
        
        if self.rng.random() < self.config.extra_field_probability:
            corrupted = self._inject_extra_field(corrupted, record_id)
        
        return corrupted
    
    def _inject_missing_field(self, record: Dict[str, Any], record_id: str, 
                              eligible_fields: List[str]) -> Dict[str, Any]:
        """Remove a random field from the record."""
        # Only consider fields that actually exist
        present_fields = [f for f in eligible_fields if f in record]
        if not present_fields:
            return record
        
        field_to_remove = self.rng.choice(present_fields)
        original_value = record.get(field_to_remove)
        
        del record[field_to_remove]
        
        self._log_issue(
            record_id=record_id,
            issue_type="missing_field",
            affected_field=field_to_remove,
            original_value=str(original_value),
            injected_value=None,
            reason_code="FIELD_OMITTED"
        )
        
        return record
    
    def _inject_null_value(self, record: Dict[str, Any], record_id: str,
                           eligible_fields: List[str]) -> Dict[str, Any]:
        """Replace a field value with None/null."""
        present_fields = [f for f in eligible_fields if f in record]
        if not present_fields:
            return record
        
        field_to_null = self.rng.choice(present_fields)
        original_value = record.get(field_to_null)
        
        record[field_to_null] = None
        
        self._log_issue(
            record_id=record_id,
            issue_type="null_value",
            affected_field=field_to_null,
            original_value=str(original_value),
            injected_value="null",
            reason_code="NULL_INJECTION"
        )
        
        return record
    
    def _inject_malformed_timestamp(self, record: Dict[str, Any], record_id: str,
                                     field_name: str) -> Dict[str, Any]:
        """Replace timestamp with malformed value."""
        if field_name not in record:
            return record
        
        original_value = record[field_name]
        
        # Various malformed timestamp patterns
        malformed_patterns = [
            "2024-13-01T00:00:00Z",  # Invalid month
            "2024-01-32T00:00:00Z",  # Invalid day
            "2024-01-01T25:00:00Z",  # Invalid hour
            "2024-01-01 00:00:00",   # Missing timezone
            "not-a-timestamp",       # Complete garbage
            "2024/01/01 00:00:00",   # Wrong separator
        ]
        
        record[field_name] = self.rng.choice(malformed_patterns)
        
        self._log_issue(
            record_id=record_id,
            issue_type="malformed_timestamp",
            affected_field=field_name,
            original_value=str(original_value),
            injected_value=record[field_name],
            reason_code="TIMESTAMP_MALFORMED"
        )
        
        return record
    
    def _inject_invalid_enum(self, record: Dict[str, Any], record_id: str,
                             field_name: str) -> Dict[str, Any]:
        """Replace enum field with invalid value."""
        if field_name not in record:
            return record
        
        original_value = record[field_name]
        
        # Invalid enum values for event_type
        invalid_values = [
            "UNKNOWN_EVENT",
            "invalid-type",
            "123",
            "",
            "NaN",
        ]
        
        record[field_name] = self.rng.choice(invalid_values)
        
        self._log_issue(
            record_id=record_id,
            issue_type="invalid_enum",
            affected_field=field_name,
            original_value=str(original_value),
            injected_value=record[field_name],
            reason_code="ENUM_INVALID"
        )
        
        return record
    
    def _inject_extra_field(self, record: Dict[str, Any], record_id: str) -> Dict[str, Any]:
        """Add unexpected extra fields to the record."""
        extra_fields = [
            ("legacy_id", "LEGACY_" + str(self.rng.randint(10000, 99999))),
            ("debug_flag", True),
            ("internal_notes", "System migration artifact"),
            ("_metadata", {"source": "legacy_system", "version": "1.0"}),
            ("temp_field", None),
            ("extra_timestamp", datetime.now().isoformat()),
        ]
        
        # Choose random field by index
        idx = self.rng.randint(0, len(extra_fields))
        field_name, field_value = extra_fields[idx]
        record[field_name] = field_value
        
        self._log_issue(
            record_id=record_id,
            issue_type="extra_field",
            affected_field=field_name,
            original_value=None,
            injected_value=str(field_value),
            reason_code="EXTRA_FIELD_ADDED"
        )
        
        return record
    
    def _inject_boundary_violation(self, record: Dict[str, Any], record_id: str,
                                   field_name: str) -> Dict[str, Any]:
        """Inject timestamp that's outside the valid interval bounds."""
        if field_name not in record:
            return record
        
        original_value = record[field_name]
        
        # Create timestamps that are outside reasonable bounds
        violations = [
            "2024-01-01T00:00:00Z",  # Way in the past
            "2030-01-01T00:00:00Z",  # Way in the future
            (datetime.now() - timedelta(days=365)).isoformat() + "Z",  # 1 year ago
        ]
        
        # Choose random violation by index
        idx = self.rng.randint(0, len(violations))
        record[field_name] = violations[idx]
        
        self._log_issue(
            record_id=record_id,
            issue_type="boundary_violation",
            affected_field=field_name,
            original_value=str(original_value),
            injected_value=record[field_name],
            reason_code="TIMESTAMP_OUT_OF_BOUNDS"
        )
        
        return record
    
    def _log_issue(self, record_id: str, issue_type: str, affected_field: str,
                   original_value: Optional[str], injected_value: Optional[str],
                   reason_code: str) -> None:
        """Log an injected quality issue."""
        issue = InjectedIssue(
            record_id=record_id,
            issue_type=issue_type,
            affected_field=affected_field,
            original_value=original_value,
            injected_value=injected_value,
            reason_code=reason_code
        )
        
        self.issues_log.append(issue)
        
        if self.config.log_injected_issues:
            logger.warning(
                f"Quality issue injected: {issue_type} in {record_id}.{affected_field} "
                f"({reason_code}): {original_value} → {injected_value}"
            )
    
    def get_issues_summary(self) -> Dict[str, int]:
        """Get summary statistics of injected issues."""
        summary = {}
        for issue in self.issues_log:
            summary[issue.issue_type] = summary.get(issue.issue_type, 0) + 1
        return summary
    
    def reset_log(self) -> None:
        """Clear the issues log."""
        self.issues_log = []
