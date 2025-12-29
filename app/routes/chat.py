from fastapi import APIRouter, HTTPException, status
from typing import Optional, Dict, Any, List
import re

from app.data import get_user_by_id, get_all_destinations
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_service import ai_service

router = APIRouter(prefix="/api", tags=["chat"])


# Emotion keywords mapping
EMOTION_KEYWORDS = {
    "happy": ["happy", "joy", "joyful", "excited", "cheerful", "glad", "delighted", "thrilled", "wonderful"],
    "sad": ["sad", "lonely", "down", "depressed", "blue", "upset", "unhappy", "gloomy", "melancholy"],
    "stressed": ["stress", "stressed", "anxiety", "anxious", "worried", "tense", "overwhelmed", "tired", "exhausted"],
    "excited": ["excited", "adventure", "adventurous", "energetic", "pump", "pumped", "thrilled", "eager"],
    "romantic": ["romantic", "romance", "love", "couple", "date", "honeymoon", "intimate"],
    "peaceful": ["peace", "peaceful", "calm", "relax", "quiet", "tranquil", "serene", "meditate"]
}

# Intent keywords mapping
INTENT_KEYWORDS = {
    "destination_suggestion": ["suggest", "recommend", "where", "place", "destination", "visit", "see", "go", "show me"],
    "itinerary_creation": ["itinerary", "plan", "schedule", "route", "organize", "day trip", "trip plan"],
    "photo_spots": ["photo", "instagram", "picture", "selfie", "photography", "camera", "scenic"],
    "directions": ["direction", "how to get", "how do i get", "way to", "navigate", "location", "address"],
    "cost_info": ["cost", "price", "expensive", "cheap", "budget", "money", "afford"],
    "time_info": ["time", "how long", "duration", "hours", "minutes", "open", "close"]
}


def detect_emotion(message: str) -> Optional[str]:
    """
    Detect emotion from user message using keyword matching.
    
    Args:
        message: User's message text
    
    Returns:
        Detected emotion string or None
    """
    message_lower = message.lower()
    
    for emotion, keywords in EMOTION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in message_lower:
                return emotion
    
    return None


def detect_intent(message: str) -> List[str]:
    """
    Detect user intent from message using keyword matching.
    
    Args:
        message: User's message text
    
    Returns:
        List of detected intents
    """
    message_lower = message.lower()
    detected_intents = []
    
    for intent, keywords in INTENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in message_lower:
                if intent not in detected_intents:
                    detected_intents.append(intent)
                break
    
    # Default intent if nothing detected
    if not detected_intents:
        detected_intents.append("general_query")
    
    return detected_intents


def get_user_context(user: dict) -> Dict[str, Any]:
    """Build user context dictionary for AI service."""
    return {
        "personality_type": user["personality_type"],
        "travel_style": user["travel_style"],
        "transport_type": user["transport_type"],
        "has_itinerary": user["has_itinerary"]
    }


@router.post("/chat", response_model=ChatResponse)
def chat_with_assistant(request: ChatRequest):
    """
    Chat with AI travel assistant. Detects intent and emotion, provides personalized responses.
    
    Supported intents:
    - destination_suggestion: Recommend places to visit
    - itinerary_creation: Create day plans
    - photo_spots: Find Instagram-worthy locations
    - directions: Get navigation help
    - cost_info: Budget and pricing information
    - time_info: Duration and timing details
    
    Detects emotions: happy, sad, stressed, excited, romantic, peaceful
    """
    # Validate user exists
    user = get_user_by_id(request.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {request.user_id} not found"
        )
    
    # Detect emotion from message
    detected_emotion = detect_emotion(request.message)
    
    # Detect intent from message
    detected_intents = detect_intent(request.message)
    
    # Build user context
    user_context = get_user_context(user)
    
    # Initialize response components
    ai_response = ""
    suggested_destinations = None
    itinerary = None
    
    try:
        # Handle emotion-based destination suggestions
        if detected_emotion:
            # Get destinations from mock data
            destinations = get_all_destinations()
            destinations_list = [
                {
                    "id": dest["id"],
                    "name": dest["name"],
                    "location": dest["location"],
                    "category": dest["category"],
                    "photo_spot": dest["photo_spot"],
                    "estimated_cost": dest["estimated_cost"],
                    "estimated_time": dest["estimated_time"],
                    "description": dest["description"]
                }
                for dest in destinations[:15]
            ]
            
            # Get emotion-based suggestions from AI
            emotion_suggestions = ai_service.suggest_destinations_by_emotion(
                detected_emotion,
                destinations_list
            )
            
            # Format suggested destinations
            suggested_destinations = []
            for rec in emotion_suggestions.get("recommendations", [])[:5]:
                # Find matching destination
                matching_dest = next(
                    (d for d in destinations_list if d["name"] == rec.get("destination_name")),
                    None
                )
                if matching_dest:
                    suggested_destinations.append({
                        "id": matching_dest["id"],
                        "name": matching_dest["name"],
                        "location": matching_dest["location"],
                        "reason": rec.get("reason", "Suitable for your mood"),
                        "priority": rec.get("priority", "medium"),
                        "cost": matching_dest["estimated_cost"],
                        "time": matching_dest["estimated_time"],
                        "photo_spot": matching_dest["photo_spot"]
                    })
            
            # Build response with emotion context
            emotion_context = f"\n\nEmotion detected: {detected_emotion}. {emotion_suggestions.get('emotion_analysis', '')}"
            ai_response = ai_service.chat_with_gemini(
                request.message + emotion_context,
                user_context
            )
        
        # Handle photo spot requests
        elif "photo_spots" in detected_intents:
            photo_destinations = db.query(Destination).filter(
                Destination.photo_spot == True
            ).limit(10).all()
            
            suggested_destinations = [
                {
                    "id": dest.id,
                    "name": dest.name,
                    "location": dest.location,
                    "category": dest.category,
                    "reason": "Popular photo spot with stunning views",
                    "priority": "high" if dest.category == "famous" else "medium",
                    "cost": dest.estimated_cost,
                    "time": dest.estimated_time,
                    "photo_spot": True
                }
                for dest in photo_destinations
            ]
            
            ai_response = ai_service.chat_with_gemini(
                request.message + "\n\nContext: User is looking for photo spots in Da Lat.",
                user_context
            )
        
        # Handle destination suggestions
        elif "destination_suggestion" in detected_intents:
            # Get destinations based on user preferences
            all_destinations = get_all_destinations()
            
            # Filter by personality and travel style
            if user["personality_type"] == "introvert":
                # Prefer less crowded, peaceful spots
                all_destinations = [d for d in all_destinations if d["category"] == "local"]
            
            suggested_destinations = [
                {
                    "id": dest["id"],
                    "name": dest["name"],
                    "location": dest["location"],
                    "category": dest["category"],
                    "reason": f"Matches your {user['personality_type']} personality",
                    "priority": "high",
                    "cost": dest["estimated_cost"],
                    "time": dest["estimated_time"],
                    "photo_spot": dest["photo_spot"]
                }
                for dest in all_destinations[:5]
            ]
            
            ai_response = ai_service.chat_with_gemini(request.message, user_context)
        
        # Handle general queries
        else:
            ai_response = ai_service.chat_with_gemini(request.message, user_context)
        
        # Build response
        return ChatResponse(
            response=ai_response,
            suggested_destinations=suggested_destinations,
            itinerary=None,  # Can be enhanced later with itinerary generation
            metadata={
                "detected_emotion": detected_emotion,
                "detected_intents": detected_intents,
                "user_personality": user["personality_type"],
                "user_travel_style": user["travel_style"]
            }
        )
    
    except Exception as e:
        # Fallback response if AI service fails
        fallback_response = f"I'm here to help you explore Da Lat! I detected you're interested in {', '.join(detected_intents)}. "
        
        if detected_emotion:
            fallback_response += f"I sense you're feeling {detected_emotion}. "
        
        fallback_response += "Could you tell me more about what you'd like to do in Da Lat?"
        
        return ChatResponse(
            response=fallback_response,
            suggested_destinations=suggested_destinations,
            itinerary=None,
            metadata={
                "detected_emotion": detected_emotion,
                "detected_intents": detected_intents,
                "error": str(e)
            }
        )
