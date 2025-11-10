"""Configuration models and validation for data generators."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re
from .quality_injection import QualityInjectionConfig


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
    seed: Optional[int] = Field(default=None, description="Random seed for reproducibility")
    quality_injection: QualityInjectionConfig = Field(
        default_factory=QualityInjectionConfig,
        description="Data quality injection configuration for testing"
    )
    
    @field_validator('company_onboarding_interval')
    @classmethod
    def validate_iso8601_duration(cls, v: str) -> str:
        """Validate ISO8601 duration format."""
        # Simple regex for common duration patterns: PT#H, PT#M, PT#H#M
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
