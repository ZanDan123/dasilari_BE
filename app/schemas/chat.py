from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User's chat message")
    user_id: int = Field(..., gt=0, description="ID of the user sending the message")


class ItineraryItem(BaseModel):
    destination_id: int
    destination_name: str
    visit_date: date
    time_slot: str
    emotion_tag: Optional[str] = None


class ChatResponse(BaseModel):
    response: str = Field(..., description="AI assistant's response message")
    suggested_destinations: Optional[List[Dict[str, Any]]] = Field(
        default=None, 
        description="List of suggested destinations with details"
    )
    itinerary: Optional[List[ItineraryItem]] = Field(
        default=None, 
        description="Proposed itinerary items"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata about the response"
    )
