from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import date, datetime

from app.database import get_db
from app.models.user import User
from app.models.destination import Destination
from app.models.itinerary import Itinerary
from app.services.ai_service import ai_service

router = APIRouter(prefix="/api/itineraries", tags=["itineraries"])


class ItineraryGenerateRequest(BaseModel):
    user_id: int = Field(..., gt=0)
    emotion: Optional[str] = Field(None, description="User's current emotion")
    destination_ids: List[int] = Field(..., min_items=1, description="List of destination IDs to include")
    visit_date: date = Field(..., description="Date for the itinerary")


@router.post("/generate", status_code=status.HTTP_201_CREATED)
def generate_itinerary(
    request: ItineraryGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Generate complete itinerary with time slots, costs, and locations using AI.
    Saves itinerary to database and returns formatted response.
    
    Args:
        user_id: ID of the user
        emotion: Optional emotion tag (happy, sad, stressed, excited)
        destination_ids: List of destination IDs to visit
        visit_date: Date for the itinerary
    
    Returns:
        Generated itinerary with schedule, costs, and saved database entries
    """
    # Validate user exists
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {request.user_id} not found"
        )
    
    # Validate and fetch destinations
    destinations = db.query(Destination).filter(
        Destination.id.in_(request.destination_ids)
    ).all()
    
    if len(destinations) != len(request.destination_ids):
        found_ids = [d.id for d in destinations]
        missing_ids = set(request.destination_ids) - set(found_ids)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destinations not found: {missing_ids}"
        )
    
    # Prepare user preferences for AI
    user_preferences = {
        "personality_type": user.personality_type,
        "travel_style": user.travel_style,
        "transport_type": user.transport_type
    }
    
    # Prepare destination data for AI
    selected_destinations = [
        {
            "id": dest.id,
            "name": dest.name,
            "location": dest.location,
            "estimated_cost": dest.estimated_cost or 0,
            "estimated_time": dest.estimated_time or 90,
            "category": dest.category,
            "photo_spot": dest.photo_spot,
            "description": dest.description
        }
        for dest in destinations
    ]
    
    try:
        # Generate itinerary using AI service
        ai_itinerary = ai_service.generate_itinerary(
            user_preferences,
            selected_destinations
        )
        
        # Save itinerary items to database
        saved_itineraries = []
        destination_lookup = {dest.id: dest for dest in destinations}
        
        for schedule_item in ai_itinerary.get("schedule", []):
            # Find matching destination by name
            destination_name = schedule_item.get("destination")
            matching_dest = next(
                (d for d in destinations if d.name == destination_name),
                None
            )
            
            if matching_dest:
                # Create itinerary entry
                itinerary_entry = Itinerary(
                    user_id=request.user_id,
                    destination_id=matching_dest.id,
                    visit_date=request.visit_date,
                    time_slot=schedule_item.get("time_slot", "morning"),
                    emotion_tag=request.emotion
                )
                
                db.add(itinerary_entry)
                saved_itineraries.append({
                    "destination_id": matching_dest.id,
                    "destination_name": matching_dest.name,
                    "time_slot": schedule_item.get("time_slot"),
                    "time_range": schedule_item.get("time_range", ""),
                    "activity": schedule_item.get("activity", ""),
                    "duration": schedule_item.get("duration", ""),
                    "cost": schedule_item.get("cost", 0),
                    "directions": schedule_item.get("directions", ""),
                    "tips": schedule_item.get("tips", "")
                })
        
        # Commit all itinerary entries
        db.commit()
        
        # Update user's has_itinerary status
        user.has_itinerary = True
        db.commit()
        
        # Build complete response
        return {
            "status": "success",
            "message": "Itinerary generated and saved successfully",
            "user_id": request.user_id,
            "visit_date": request.visit_date.isoformat(),
            "emotion_tag": request.emotion,
            "itinerary": {
                "title": ai_itinerary.get("itinerary_title", "Your Da Lat Day Trip"),
                "total_estimated_cost": ai_itinerary.get("total_estimated_cost", 0),
                "total_duration": ai_itinerary.get("total_duration", "Full day"),
                "schedule": saved_itineraries,
                "meal_suggestions": ai_itinerary.get("meal_suggestions", [])
            },
            "destinations_count": len(saved_itineraries)
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate itinerary: {str(e)}"
        )


@router.get("/{user_id}")
def get_user_itineraries(
    user_id: int,
    visit_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve saved itineraries for a user with destination details and total cost calculation.
    
    Args:
        user_id: ID of the user
        visit_date: Optional date filter for specific itinerary
    
    Returns:
        User's itineraries with complete destination information and cost totals
    """
    # Validate user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Query itineraries with destination join
    query = db.query(Itinerary, Destination).join(
        Destination, Itinerary.destination_id == Destination.id
    ).filter(Itinerary.user_id == user_id)
    
    # Apply date filter if provided
    if visit_date:
        query = query.filter(Itinerary.visit_date == visit_date)
    
    # Order by date and time slot
    time_slot_order = {
        "morning": 1,
        "afternoon": 2,
        "evening": 3
    }
    
    results = query.order_by(Itinerary.visit_date.desc()).all()
    
    if not results:
        return {
            "user_id": user_id,
            "user_name": user.name,
            "itineraries": [],
            "total_itineraries": 0,
            "message": "No itineraries found"
        }
    
    # Group itineraries by date
    itineraries_by_date = {}
    
    for itinerary, destination in results:
        date_key = itinerary.visit_date.isoformat()
        
        if date_key not in itineraries_by_date:
            itineraries_by_date[date_key] = {
                "visit_date": date_key,
                "emotion_tag": itinerary.emotion_tag,
                "destinations": [],
                "total_cost": 0.0,
                "total_time": 0,
                "created_at": itinerary.created_at.isoformat()
            }
        
        # Add destination to this date's itinerary
        dest_cost = destination.estimated_cost or 0.0
        dest_time = destination.estimated_time or 0
        
        itineraries_by_date[date_key]["destinations"].append({
            "itinerary_id": itinerary.id,
            "destination": {
                "id": destination.id,
                "name": destination.name,
                "location": destination.location,
                "category": destination.category,
                "photo_spot": destination.photo_spot,
                "estimated_cost": dest_cost,
                "estimated_time": dest_time,
                "description": destination.description
            },
            "time_slot": itinerary.time_slot,
            "time_slot_order": time_slot_order.get(itinerary.time_slot, 0)
        })
        
        itineraries_by_date[date_key]["total_cost"] += dest_cost
        itineraries_by_date[date_key]["total_time"] += dest_time
    
    # Sort destinations within each date by time slot
    for date_key in itineraries_by_date:
        itineraries_by_date[date_key]["destinations"].sort(
            key=lambda x: x["time_slot_order"]
        )
        # Remove time_slot_order from response
        for dest in itineraries_by_date[date_key]["destinations"]:
            del dest["time_slot_order"]
    
    # Convert to list
    itineraries_list = list(itineraries_by_date.values())
    
    # Calculate overall statistics
    total_cost = sum(itin["total_cost"] for itin in itineraries_list)
    total_destinations = sum(len(itin["destinations"]) for itin in itineraries_list)
    
    return {
        "user_id": user_id,
        "user_name": user.name,
        "user_preferences": {
            "personality_type": user.personality_type,
            "travel_style": user.travel_style,
            "transport_type": user.transport_type
        },
        "itineraries": itineraries_list,
        "summary": {
            "total_itineraries": len(itineraries_list),
            "total_destinations": total_destinations,
            "total_cost": round(total_cost, 2),
            "average_cost_per_day": round(total_cost / len(itineraries_list), 2) if itineraries_list else 0
        }
    }
