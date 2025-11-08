"""Unit tests for configuration validation."""

import pytest
from pydantic import ValidationError

from src.generators.config import Config


def test_valid_config():
    """Test valid configuration parses correctly."""
    config_data = {
        "number_of_companies": 100,
        "drivers_per_company": 10,
        "event_rate_per_driver": 3.5,
        "company_onboarding_interval": "PT1H",
        "seed": 42
    }
    config = Config(**config_data)
    assert config.number_of_companies == 100
    assert config.drivers_per_company == 10
    assert config.event_rate_per_driver == 3.5
    assert config.company_onboarding_interval == "PT1H"
    assert config.seed == 42


def test_missing_required_field():
    """Test missing required field raises ValidationError."""
    config_data = {
        "drivers_per_company": 10,
        "event_rate_per_driver": 3.5,
        "company_onboarding_interval": "PT1H"
        # Missing number_of_companies
    }
    with pytest.raises(ValidationError) as exc_info:
        Config(**config_data)
    assert "number_of_companies" in str(exc_info.value)


def test_negative_number_of_companies():
    """Test negative number_of_companies raises ValidationError."""
    config_data = {
        "number_of_companies": -10,
        "drivers_per_company": 10,
        "event_rate_per_driver": 3.5,
        "company_onboarding_interval": "PT1H"
    }
    with pytest.raises(ValidationError) as exc_info:
        Config(**config_data)
    assert "number_of_companies" in str(exc_info.value)


def test_zero_drivers_per_company():
    """Test zero drivers_per_company raises ValidationError."""
    config_data = {
        "number_of_companies": 100,
        "drivers_per_company": 0,
        "event_rate_per_driver": 3.5,
        "company_onboarding_interval": "PT1H"
    }
    with pytest.raises(ValidationError) as exc_info:
        Config(**config_data)
    assert "drivers_per_company" in str(exc_info.value)


def test_negative_event_rate():
    """Test negative event_rate_per_driver raises ValidationError."""
    config_data = {
        "number_of_companies": 100,
        "drivers_per_company": 10,
        "event_rate_per_driver": -1.0,
        "company_onboarding_interval": "PT1H"
    }
    with pytest.raises(ValidationError) as exc_info:
        Config(**config_data)
    assert "event_rate_per_driver" in str(exc_info.value)


def test_invalid_iso8601_duration():
    """Test invalid ISO8601 duration format raises ValidationError."""
    config_data = {
        "number_of_companies": 100,
        "drivers_per_company": 10,
        "event_rate_per_driver": 3.5,
        "company_onboarding_interval": "1 hour"  # Invalid format
    }
    with pytest.raises(ValidationError) as exc_info:
        Config(**config_data)
    assert "company_onboarding_interval" in str(exc_info.value)
    assert "ISO8601" in str(exc_info.value)


def test_empty_duration():
    """Test empty duration (PT) raises ValidationError."""
    config_data = {
        "number_of_companies": 100,
        "drivers_per_company": 10,
        "event_rate_per_driver": 3.5,
        "company_onboarding_interval": "PT"  # Empty duration
    }
    with pytest.raises(ValidationError) as exc_info:
        Config(**config_data)
    assert "company_onboarding_interval" in str(exc_info.value)


def test_valid_duration_formats():
    """Test various valid ISO8601 duration formats."""
    valid_durations = ["PT1H", "PT30M", "PT1H30M", "PT90M", "PT3600S"]
    for duration in valid_durations:
        config_data = {
            "number_of_companies": 100,
            "drivers_per_company": 10,
            "event_rate_per_driver": 3.5,
            "company_onboarding_interval": duration
        }
        config = Config(**config_data)
        assert config.company_onboarding_interval == duration


def test_optional_seed():
    """Test seed is optional and defaults to None."""
    config_data = {
        "number_of_companies": 100,
        "drivers_per_company": 10,
        "event_rate_per_driver": 3.5,
        "company_onboarding_interval": "PT1H"
    }
    config = Config(**config_data)
    assert config.seed is None
