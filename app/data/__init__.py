# Mock data initialization
from app.data.mock_destinations import MOCK_DESTINATIONS, get_all_destinations, get_destination_by_id, filter_destinations, get_photo_spots
from app.data.mock_users import MOCK_USERS, get_all_users, get_user_by_id, create_user, filter_users_by_preferences
from app.data.mock_itineraries import MOCK_ITINERARIES, get_all_itineraries, get_itinerary_by_id, get_itineraries_by_user, create_itinerary, delete_itinerary, filter_itineraries

__all__ = [
    "MOCK_DESTINATIONS",
    "MOCK_USERS", 
    "MOCK_ITINERARIES",
    "get_all_destinations",
    "get_destination_by_id",
    "filter_destinations",
    "get_photo_spots",
    "get_all_users",
    "get_user_by_id",
    "create_user",
    "filter_users_by_preferences",
    "get_all_itineraries",
    "get_itinerary_by_id",
    "get_itineraries_by_user",
    "create_itinerary",
    "delete_itinerary",
    "filter_itineraries"
]
