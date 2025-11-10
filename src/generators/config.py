"""Configuration models and validation for data generators."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import timedelta
import re
import isodate
from .quality_injection import QualityInjectionConfig


class EmulatedModeConfig(BaseModel):
    """
    Configuration for emulated fast-cadence generation mode.
    
    Used for development/testing to observe pipeline in near real-time.
    Generates small batches (5-20 records) at rapid intervals (5-10 seconds).
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
    
    @field_validator('events_per_batch_max')
    @classmethod
    def validate_event_range(cls, v: int, info) -> int:
        """Validate max >= min for event range."""
        if 'events_per_batch_min' in info.data:
            min_val = info.data['events_per_batch_min']
            if v < min_val:
                raise ValueError(f"events_per_batch_max ({v}) must be >= events_per_batch_min ({min_val})")
        return v


class Config(BaseModel):
    """
    Generator configuration with validation.
    
    Validates:
    - number_of_companies: Must be > 0
    - drivers_per_company: Must be > 0
    - event_rate_per_driver: Must be > 0
    - company_onboarding_interval: Must be valid ISO8601 duration (e.g., PT1H, PT30M)
    - seed: Optional random seed
    - quality_injection: Data quality issue injection configuration
    """
    
    number_of_companies: int = Field(gt=0, description="Number of companies to generate")
    drivers_per_company: int = Field(gt=0, description="Number of drivers per company")
    event_rate_per_driver: float = Field(gt=0, description="Average events per driver per 15-min interval")
    company_onboarding_interval: str = Field(description="ISO8601 duration for company onboarding cadence (e.g., PT1H)")
    driver_event_interval: str = Field(
        default="PT15M",
        description="ISO8601 duration for driver event batch cadence (e.g., PT15M, PT10S)"
    )
    seed: Optional[int] = Field(default=None, description="Random seed for reproducibility")
    quality_injection: QualityInjectionConfig = Field(
        default_factory=QualityInjectionConfig,
        description="Data quality injection configuration for testing"
    )
    emulated_mode: EmulatedModeConfig = Field(
        default_factory=EmulatedModeConfig,
        description="Emulated fast-cadence mode configuration"
    )
    
    @property
    def active_company_interval(self) -> str:
        """Return company interval based on mode (emulated or production)."""
        if self.emulated_mode.enabled:
            return self.emulated_mode.company_batch_interval
        return self.company_onboarding_interval
    
    @property
    def active_driver_interval(self) -> str:
        """Return driver interval based on mode (emulated or production)."""
        if self.emulated_mode.enabled:
            return self.emulated_mode.driver_batch_interval
        return self.driver_event_interval
    
    @property
    def active_company_count(self) -> int:
        """Return company count based on mode (emulated or production)."""
        if self.emulated_mode.enabled:
            return self.emulated_mode.companies_per_batch
        return self.number_of_companies
    
    @field_validator('company_onboarding_interval', 'driver_event_interval')
    @classmethod
    def validate_iso8601_duration(cls, v: str) -> str:
        """Validate ISO8601 duration format."""
        # Simple regex for common duration patterns: PT#H, PT#M, PT#S
        pattern = r'^PT(\d+H)?(\d+M)?(\d+S)?$'
        if not re.match(pattern, v):
            raise ValueError(
                f"Invalid ISO8601 duration: {v}. Expected format like PT1H, PT30M, PT1H30M"
            )
        # Ensure at least one component is present
        if v == 'PT':
            raise ValueError("Duration must specify at least hours, minutes, or seconds")
        return v
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "number_of_companies": 100,
                    "drivers_per_company": 10,
                    "event_rate_per_driver": 3.5,
                    "company_onboarding_interval": "PT1H",
                    "seed": 42
                }
            ]
        }
    }
