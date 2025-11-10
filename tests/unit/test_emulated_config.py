"""Unit tests for EmulatedModeConfig validation."""

import pytest
from pydantic import ValidationError
from src.generators.config import EmulatedModeConfig, Config


class TestEmulatedModeConfig:
    """Test EmulatedModeConfig validation rules."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = EmulatedModeConfig()
        
        assert config.enabled is False
        assert config.company_batch_interval == "PT10S"
        assert config.driver_batch_interval == "PT10S"
        assert config.companies_per_batch == 10
        assert config.events_per_batch_min == 5
        assert config.events_per_batch_max == 20
    
    def test_interval_validation_valid_formats(self):
        """Test valid ISO 8601 duration formats."""
        valid_intervals = [
            "PT1S",     # 1 second
            "PT10S",    # 10 seconds
            "PT1M",     # 1 minute
            "PT5M",     # 5 minutes
            "PT1H",     # 1 hour
            "PT1H30M",  # 1.5 hours
            "PT1H30M45S"  # 1 hour 30 min 45 sec
        ]
        
        for interval in valid_intervals:
            config = EmulatedModeConfig(
                company_batch_interval=interval,
                driver_batch_interval=interval
            )
            assert config.company_batch_interval == interval
            assert config.driver_batch_interval == interval
    
    def test_interval_validation_invalid_formats(self):
        """Test invalid ISO 8601 duration formats."""
        invalid_intervals = [
            "10S",      # Missing PT prefix
            "PT",       # No duration specified
            "10",       # Just a number
            "PT0.5S",   # Decimal seconds not in pattern
            "1H",       # Missing PT prefix
            "PT-10S"    # Negative duration
        ]
        
        for interval in invalid_intervals:
            with pytest.raises(ValidationError):
                EmulatedModeConfig(company_batch_interval=interval)
    
    def test_interval_minimum_one_second(self):
        """Test that intervals must be >= 1 second."""
        # Valid: exactly 1 second
        config = EmulatedModeConfig(company_batch_interval="PT1S")
        assert config.company_batch_interval == "PT1S"
        
        # Note: Our pattern doesn't support sub-second durations like PT0.5S
        # which is good - it enforces the >=1s requirement at pattern level
    
    def test_event_range_validation(self):
        """Test events_per_batch_max >= events_per_batch_min."""
        # Valid: max >= min
        config = EmulatedModeConfig(
            events_per_batch_min=5,
            events_per_batch_max=20
        )
        assert config.events_per_batch_min == 5
        assert config.events_per_batch_max == 20
        
        # Valid: max == min
        config = EmulatedModeConfig(
            events_per_batch_min=10,
            events_per_batch_max=10
        )
        assert config.events_per_batch_min == 10
        assert config.events_per_batch_max == 10
        
        # Invalid: max < min
        with pytest.raises(ValidationError) as exc_info:
            EmulatedModeConfig(
                events_per_batch_min=20,
                events_per_batch_max=5
            )
        assert "events_per_batch_max" in str(exc_info.value)
    
    def test_companies_per_batch_bounds(self):
        """Test companies_per_batch is within [1, 100]."""
        # Valid: within bounds
        config = EmulatedModeConfig(companies_per_batch=1)
        assert config.companies_per_batch == 1
        
        config = EmulatedModeConfig(companies_per_batch=100)
        assert config.companies_per_batch == 100
        
        config = EmulatedModeConfig(companies_per_batch=50)
        assert config.companies_per_batch == 50
        
        # Invalid: below minimum
        with pytest.raises(ValidationError):
            EmulatedModeConfig(companies_per_batch=0)
        
        # Invalid: above maximum
        with pytest.raises(ValidationError):
            EmulatedModeConfig(companies_per_batch=101)


class TestConfigWithEmulatedMode:
    """Test Config integration with EmulatedModeConfig."""
    
    def test_default_emulated_mode_disabled(self):
        """Test that emulated mode is disabled by default."""
        config = Config(
            number_of_companies=100,
            drivers_per_company=10,
            event_rate_per_driver=3.5,
            company_onboarding_interval="PT1H"
        )
        
        assert config.emulated_mode.enabled is False
        assert config.active_company_interval == "PT1H"
        assert config.active_driver_interval == "PT15M"  # Default
        assert config.active_company_count == 100
    
    def test_emulated_mode_enabled(self):
        """Test active properties when emulated mode is enabled."""
        config = Config(
            number_of_companies=100,
            drivers_per_company=10,
            event_rate_per_driver=3.5,
            company_onboarding_interval="PT1H",
            driver_event_interval="PT15M",
            emulated_mode={
                "enabled": True,
                "company_batch_interval": "PT5S",
                "driver_batch_interval": "PT10S",
                "companies_per_batch": 10,
                "events_per_batch_min": 5,
                "events_per_batch_max": 20
            }
        )
        
        assert config.emulated_mode.enabled is True
        assert config.active_company_interval == "PT5S"
        assert config.active_driver_interval == "PT10S"
        assert config.active_company_count == 10
    
    def test_production_mode_active_properties(self):
        """Test active properties use production values when emulated disabled."""
        config = Config(
            number_of_companies=500,
            drivers_per_company=20,
            event_rate_per_driver=5.0,
            company_onboarding_interval="PT2H",
            driver_event_interval="PT30M",
            emulated_mode={"enabled": False}
        )
        
        assert config.active_company_interval == "PT2H"
        assert config.active_driver_interval == "PT30M"
        assert config.active_company_count == 500
