"""Unit tests for quality injection functionality."""

import numpy as np
import pytest
from datetime import datetime, timezone

from src.generators.quality_injection import QualityInjectionConfig, InjectedIssue
from src.generators.injector import QualityInjector


class TestQualityInjectionConfig:
    """Test configuration model validation."""
    
    def test_default_config(self):
        """Default config should be disabled with zero error rate."""
        config = QualityInjectionConfig()
        assert config.enabled is False
        assert config.error_rate == 0.0
    
    def test_enabled_config(self):
        """Can create enabled config with custom probabilities."""
        config = QualityInjectionConfig(
            enabled=True,
            error_rate=0.2,
            missing_field_probability=0.5,
            null_value_probability=0.3
        )
        assert config.enabled is True
        assert config.error_rate == 0.2
        assert config.missing_field_probability == 0.5
    
    def test_probability_validation(self):
        """Probabilities must be in [0, 1] range."""
        with pytest.raises(ValueError):
            QualityInjectionConfig(error_rate=-0.1)
        
        with pytest.raises(ValueError):
            QualityInjectionConfig(error_rate=1.5)


class TestQualityInjector:
    """Test quality injector logic."""
    
    def test_disabled_injector_no_changes(self):
        """Disabled injector should not modify records."""
        config = QualityInjectionConfig(enabled=False)
        rng = np.random.RandomState(42)
        injector = QualityInjector(config, rng)
        
        event = {
            "driver_id": "DRV-001",
            "event_type": "start driving",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        result = injector.inject_into_driver_event(event, "DRV-001")
        assert result == event
        assert len(injector.issues_log) == 0
    
    def test_enabled_with_zero_error_rate_no_changes(self):
        """Enabled with 0% error rate should not inject issues."""
        config = QualityInjectionConfig(enabled=True, error_rate=0.0)
        rng = np.random.RandomState(42)
        injector = QualityInjector(config, rng)
        
        event = {
            "driver_id": "DRV-001",
            "event_type": "start driving",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        result = injector.inject_into_driver_event(event, "DRV-001")
        assert result == event
        assert len(injector.issues_log) == 0
    
    def test_inject_missing_field(self):
        """Should remove fields when configured."""
        config = QualityInjectionConfig(
            enabled=True,
            error_rate=1.0,  # Always inject
            missing_field_probability=1.0,  # Always remove field
            null_value_probability=0.0,
            malformed_timestamp_probability=0.0,
            invalid_enum_probability=0.0
        )
        rng = np.random.RandomState(42)
        injector = QualityInjector(config, rng)
        
        event = {
            "driver_id": "DRV-001",
            "event_type": "start driving",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        result = injector.inject_into_driver_event(event, "DRV-001")
        
        # Should be missing one field
        assert len(result) < len(event)
        assert len(injector.issues_log) == 1
        assert injector.issues_log[0].issue_type == "missing_field"
    
    def test_inject_null_value(self):
        """Should replace values with null when configured."""
        config = QualityInjectionConfig(
            enabled=True,
            error_rate=1.0,
            missing_field_probability=0.0,
            null_value_probability=1.0,  # Always null
            malformed_timestamp_probability=0.0,
            invalid_enum_probability=0.0
        )
        rng = np.random.RandomState(42)
        injector = QualityInjector(config, rng)
        
        event = {
            "driver_id": "DRV-001",
            "event_type": "start driving",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        result = injector.inject_into_driver_event(event, "DRV-001")
        
        # Should have None/null in one field
        null_count = sum(1 for v in result.values() if v is None)
        assert null_count >= 1
        assert len(injector.issues_log) == 1
        assert injector.issues_log[0].issue_type == "null_value"
    
    def test_inject_malformed_timestamp(self):
        """Should corrupt timestamp when configured."""
        config = QualityInjectionConfig(
            enabled=True,
            error_rate=1.0,
            missing_field_probability=0.0,
            null_value_probability=0.0,
            malformed_timestamp_probability=1.0,  # Always corrupt timestamp
            invalid_enum_probability=0.0
        )
        rng = np.random.RandomState(42)
        injector = QualityInjector(config, rng)
        
        event = {
            "driver_id": "DRV-001",
            "event_type": "start driving",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        result = injector.inject_into_driver_event(event, "DRV-001")
        
        # Timestamp should be corrupted
        assert result["timestamp"] != event["timestamp"]
        assert len(injector.issues_log) == 1
        assert injector.issues_log[0].issue_type == "malformed_timestamp"
    
    def test_inject_invalid_enum(self):
        """Should corrupt enum value when configured."""
        config = QualityInjectionConfig(
            enabled=True,
            error_rate=1.0,
            missing_field_probability=0.0,
            null_value_probability=0.0,
            malformed_timestamp_probability=0.0,
            invalid_enum_probability=1.0  # Always corrupt enum
        )
        rng = np.random.RandomState(42)
        injector = QualityInjector(config, rng)
        
        event = {
            "driver_id": "DRV-001",
            "event_type": "start driving",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        result = injector.inject_into_driver_event(event, "DRV-001")
        
        # event_type should be invalid
        assert result["event_type"] != event["event_type"]
        assert result["event_type"] not in ["start driving", "stopped driving", "delivered"]
        assert len(injector.issues_log) == 1
        assert injector.issues_log[0].issue_type == "invalid_enum"
    
    def test_company_injection(self):
        """Should inject issues into company records."""
        config = QualityInjectionConfig(
            enabled=True,
            error_rate=1.0,
            null_value_probability=1.0,
            inject_in_companies=True
        )
        rng = np.random.RandomState(42)
        injector = QualityInjector(config, rng)
        
        company = {
            "company_id": "COMP-001",
            "company_name": "Test Corp",
            "onboarded_at": "2024-01-01T00:00:00Z"
        }
        
        result = injector.inject_into_company(company)
        
        # Should have at least one null value
        null_count = sum(1 for v in result.values() if v is None)
        assert null_count >= 1
        assert len(injector.issues_log) >= 1
    
    def test_issues_summary(self):
        """Should provide summary statistics of injected issues."""
        config = QualityInjectionConfig(
            enabled=True,
            error_rate=1.0,
            null_value_probability=1.0
        )
        rng = np.random.RandomState(42)
        injector = QualityInjector(config, rng)
        
        # Inject issues in multiple events
        for i in range(5):
            event = {
                "driver_id": f"DRV-{i:03d}",
                "event_type": "start driving",
                "timestamp": "2024-01-01T12:00:00Z"
            }
            injector.inject_into_driver_event(event, f"DRV-{i:03d}")
        
        summary = injector.get_issues_summary()
        assert "null_value" in summary
        assert summary["null_value"] == 5
    
    def test_reset_log(self):
        """Should clear issues log when requested."""
        config = QualityInjectionConfig(enabled=True, error_rate=1.0, null_value_probability=1.0)
        rng = np.random.RandomState(42)
        injector = QualityInjector(config, rng)
        
        event = {"driver_id": "DRV-001", "event_type": "start driving", "timestamp": "2024-01-01T12:00:00Z"}
        injector.inject_into_driver_event(event, "DRV-001")
        
        assert len(injector.issues_log) > 0
        
        injector.reset_log()
        assert len(injector.issues_log) == 0
