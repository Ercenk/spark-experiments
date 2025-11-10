"""
Data quality injection configuration and models.

Supports configurable injection of realistic data quality issues for testing pipeline validation.
"""

from pydantic import BaseModel, Field
from typing import Dict, Optional


class QualityInjectionConfig(BaseModel):
    """
    Configuration for injecting data quality issues into generated records.
    
    Used to simulate realistic data quality problems for testing data cleansing pipelines.
    """
    
    enabled: bool = Field(default=False, description="Enable quality issue injection")
    
    # Overall error rate (probability that any given record has at least one issue)
    error_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Probability (0.0-1.0) that a record has at least one quality issue"
    )
    
    # Specific issue type probabilities (applied if error_rate triggers for a record)
    missing_field_probability: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Probability of omitting a required field"
    )
    
    null_value_probability: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Probability of injecting null for a field"
    )
    
    malformed_timestamp_probability: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Probability of malforming timestamp fields"
    )
    
    invalid_enum_probability: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Probability of using invalid enumeration values"
    )
    
    duplicate_probability: float = Field(
        default=0.05,
        ge=0.0,
        le=1.0,
        description="Probability of creating intentional duplicates"
    )
    
    extra_field_probability: float = Field(
        default=0.10,
        ge=0.0,
        le=1.0,
        description="Probability of adding unexpected extra fields"
    )
    
    boundary_violation_probability: float = Field(
        default=0.05,
        ge=0.0,
        le=1.0,
        description="Probability of timestamp outside valid interval"
    )
    
    # Scope control
    inject_in_driver_events: bool = Field(
        default=True,
        description="Apply injection to driver events"
    )
    
    inject_in_companies: bool = Field(
        default=True,
        description="Apply injection to company records"
    )
    
    # Logging
    log_injected_issues: bool = Field(
        default=True,
        description="Log each injected issue for traceability"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "enabled": True,
                    "error_rate": 0.15,
                    "missing_field_probability": 0.3,
                    "null_value_probability": 0.3,
                    "malformed_timestamp_probability": 0.2,
                    "invalid_enum_probability": 0.1,
                    "duplicate_probability": 0.05,
                    "boundary_violation_probability": 0.05,
                    "inject_in_driver_events": True,
                    "inject_in_companies": True,
                    "log_injected_issues": True
                }
            ]
        }
    }


class InjectedIssue(BaseModel):
    """Record of a single injected quality issue."""
    
    record_id: str = Field(description="Identifier of affected record")
    issue_type: str = Field(description="Type of issue (missing_field, null_value, etc.)")
    affected_field: str = Field(description="Field name affected by the issue")
    original_value: Optional[str] = Field(default=None, description="Original value before injection")
    injected_value: Optional[str] = Field(default=None, description="Value after injection (null, malformed, etc.)")
    reason_code: str = Field(description="Reason code for the injection")
