from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/api", tags=["users"])


@router.post("/survey", response_model=dict, status_code=status.HTTP_201_CREATED)
def save_user_survey(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Save user survey data including personality type, travel style, transport type, and itinerary status.
    Returns user_id and confirmation message.
    """
    try:
        # Create new user from survey data
        new_user = User(
            name=user_data.name,
            personality_type=user_data.personality_type.value,
            travel_style=user_data.travel_style.value,
            transport_type=user_data.transport_type,
            has_itinerary=user_data.has_itinerary
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "user_id": new_user.id,
            "message": "Survey data saved successfully",
            "status": "success"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save survey data: {str(e)}"
        )


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve user profile and preferences by user_id.
    Returns complete user information including personality type, travel style, and preferences.
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    return user
