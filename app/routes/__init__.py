from .users import router as users_router
from .destinations import router as destinations_router
from .chat import router as chat_router
from .itineraries import router as itineraries_router

__all__ = ["users_router", "destinations_router", "chat_router", "itineraries_router"]
