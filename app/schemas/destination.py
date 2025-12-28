from pydantic import BaseModel, Field, field_validator
from enum import Enum
from typing import Optional


class CategoryType(str, Enum):
    LOCAL = "local"
    FAMOUS = "famous"


class DestinationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    location: str = Field(..., min_length=1, max_length=200)
    category: CategoryType
    photo_spot: bool = False
    estimated_cost: Optional[float] = Field(None, ge=0, description="Cost must be non-negative")
    estimated_time: Optional[int] = Field(None, ge=0, le=1440, description="Time in minutes, max 24 hours")
    description: Optional[str] = None

    @field_validator('estimated_cost')
    @classmethod
    def validate_cost(cls, v):
        if v is not None and v < 0:
            raise ValueError('Estimated cost must be non-negative')
        return v

    @field_validator('estimated_time')
    @classmethod
    def validate_time(cls, v):
        if v is not None and (v < 0 or v > 1440):
            raise ValueError('Estimated time must be between 0 and 1440 minutes (24 hours)')
        return v


class DestinationResponse(BaseModel):
    id: int
    name: str
    location: str
    category: str
    photo_spot: bool
    estimated_cost: Optional[float]
    estimated_time: Optional[int]
    description: Optional[str]

    class Config:
        from_attributes = True
