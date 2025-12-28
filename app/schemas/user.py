from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Optional


class PersonalityType(str, Enum):
    EXTROVERT = "extrovert"
    INTROVERT = "introvert"


class TravelStyle(str, Enum):
    GROUP = "group"
    SOLO = "solo"


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    personality_type: PersonalityType
    travel_style: TravelStyle
    transport_type: str = Field(..., min_length=1)
    has_itinerary: bool = False


class UserResponse(BaseModel):
    id: int
    name: str
    personality_type: str
    travel_style: str
    transport_type: str
    has_itinerary: bool
    created_at: datetime

    class Config:
        from_attributes = True
