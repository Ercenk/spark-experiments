"""Pydantic models for company and driver event entities."""

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field
from uuid import uuid4


class Company(BaseModel):
    """
    Company onboarding record.
    
    Attributes:
        company_id: Unique company identifier (UUID)
        geography: Geographic location (fixed to 'US' in initial iteration)
        active: Company active status (always True in initial iteration)
        created_at: Timestamp of company creation (UTC)
    """
    company_id: str = Field(default_factory=lambda: str(uuid4()))
    geography: Literal["US"] = "US"
    active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "company_id": "550e8400-e29b-41d4-a716-446655440000",
                    "geography": "US",
                    "active": True,
                    "created_at": "2025-11-08T12:00:00Z"
                }
            ]
        }
    }


class BatchManifest(BaseModel):
    """
    Cumulative manifest tracking all batches.
    
    Attributes:
        last_batch_id: Most recent batch identifier
        total_events: Cumulative count of all events across batches
        last_updated: Timestamp of last manifest update
    """
    last_batch_id: str
    total_events: int
    last_updated: datetime


class DriverEventRecord(BaseModel):
    """
    Driver event record for a single event.
    
    Attributes:
        event_id: Unique event identifier (UUID)
        driver_id: Driver identifier (format: DRV-{company_id}-{seq:03d})
        company_id: Associated company identifier
        truck_id: Truck identifier (format: TRK-{seed}-{n:04d})
        event_type: Type of driving event
        timestamp: Event timestamp (UTC)
    """
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    driver_id: str
    company_id: str
    truck_id: str
    event_type: Literal["start driving", "stopped driving", "delivered"]
    timestamp: datetime
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "event_id": "123e4567-e89b-12d3-a456-426614174000",
                    "driver_id": "DRV-550e8400-e29b-41d4-a716-446655440000-001",
                    "company_id": "550e8400-e29b-41d4-a716-446655440000",
                    "truck_id": "TRK-42-0001",
                    "event_type": "start driving",
                    "timestamp": "2025-11-08T12:15:30Z"
                }
            ]
        }
    }


class DriverEventBatch(BaseModel):
    """
    Metadata for a batch of driver events.
    
    Attributes:
        batch_id: Batch identifier derived from interval_start (ISO compact format)
        interval_start: Start of 15-minute interval (aligned to 15-min multiples)
        interval_end: End of interval (interval_start + 15 minutes)
        event_count: Number of events in this batch
        seed: Random seed used for generation
        generation_time: Wall clock time when batch was generated
    """
    batch_id: str
    interval_start: datetime
    interval_end: datetime
    event_count: int
    seed: int
    generation_time: datetime = Field(default_factory=lambda: datetime.utcnow())
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "batch_id": "20251108T120000Z",
                    "interval_start": "2025-11-08T12:00:00Z",
                    "interval_end": "2025-11-08T12:15:00Z",
                    "event_count": 350,
                    "seed": 42,
                    "generation_time": "2025-11-08T12:00:05Z"
                }
            ]
        }
    }
