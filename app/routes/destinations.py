from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional, List
from app.data import get_all_destinations, filter_destinations, get_photo_spots as get_photo_spots_data
from app.schemas.destination import DestinationResponse

router = APIRouter(prefix="/api/destinations", tags=["destinations"])


@router.get("", response_model=List[DestinationResponse])
def get_destinations(
    category: Optional[str] = Query(None, description="Filter by category: local or famous"),
    photo_spot: Optional[bool] = Query(None, description="Filter by photo spot availability"),
    max_cost: Optional[float] = Query(None, description="Filter by maximum cost", ge=0)
):
    """
    List all Da Lat destinations with optional filters.
    
    Filters:
    - category: Filter by 'local' or 'famous' destinations
    - photo_spot: Filter destinations that are photo spots (true/false)
    - max_cost: Filter destinations with cost less than or equal to specified amount
    """
    destinations = filter_destinations(category=category, photo_spot=photo_spot, max_cost=max_cost)
    return destinations


@router.get("/photo-spots")
def get_photo_spots():
    """
    Get all destinations that are great photo spots with descriptions of why they are photogenic.
    Perfect for Instagram-worthy locations and photography enthusiasts.
    
    Returns destinations with photo_spot=True, including details about their visual appeal.
    """
    photo_destinations = get_photo_spots_data()
    
    if not photo_destinations:
        return {
            "message": "No photo spots found",
            "photo_spots": []
        }
    
    # Enhance with photogenic reasons
    photo_reasons = {
        "Hồ Xuân Hương": "Serene lake reflections, swan boats, and pine trees create picture-perfect scenes",
        "Lang Biang Mountain": "Panoramic mountain views, misty peaks, and sweeping valley vistas",
        "Thung Lũng Tình Yêu (Valley of Love)": "Colorful flower gardens, romantic scenery, and artistic installations",
        "The Florest": "European-style architecture, vibrant flower arrangements, and Instagram-worthy café aesthetics",
        "God Valley (Thung Lũng Vàng)": "Golden grass fields, dramatic lighting at sunset, untouched natural beauty",
        "Crazy House (Hằng Nga Villa)": "Surreal architecture, whimsical designs, unique angles and structures",
        "Datanla Waterfall": "Cascading water, lush greenery, and dramatic natural formations",
        "Trúc Lâm Zen Monastery": "Peaceful temple architecture, Tuyền Lâm Lake views, cable car perspectives",
        "Da Lat Railway Station": "French colonial charm, vintage trains, historic architectural details",
        "Bảo Đại Summer Palace": "Art Deco elegance, historical ambiance, manicured gardens",
        "XQ Historical Village": "Stunning silk embroidery art, traditional Vietnamese craftsmanship displays",
        "Linh Phước Pagoda": "Colorful mosaic details, 49-meter dragon sculpture, intricate glass work",
        "Da Lat Flower Gardens": "Vibrant flower displays, seasonal blooms, creative topiary designs",
        "Mê Linh Coffee Garden": "Scenic coffee plantations, mountain backdrop, terraced landscapes",
        "Elephant Falls": "Powerful cascades, natural rock formations, jungle surroundings",
        "Pongour Waterfall": "Seven-tiered falls, wide cascades, best during rainy season",
        "Ana Mandara Villas": "Colonial French architecture, elegant villa exteriors, luxury aesthetics",
        "Clay Tunnel (Hầm Đất Sét)": "Quirky clay sculptures, creative art installations, unique textures"
    }
    
    enhanced_spots = []
    for destination in photo_destinations:
        enhanced_spots.append({
            "id": destination["id"],
            "name": destination["name"],
            "location": destination["location"],
            "category": destination["category"],
            "estimated_cost": destination["estimated_cost"],
            "estimated_time": destination["estimated_time"],
            "description": destination["description"],
            "photogenic_features": photo_reasons.get(
                destination["name"],
                "Beautiful scenery perfect for photography and creating lasting memories"
            ),
            "photography_tips": _get_photography_tips(destination["name"], destination["category"])
        })
    
    return {
        "total_photo_spots": len(enhanced_spots),
        "photo_spots": enhanced_spots,
        "general_tips": [
            "Best lighting: Early morning (6-8 AM) or golden hour (4-6 PM)",
            "Da Lat weather can change quickly - bring protective gear for your camera",
            "Respect local customs and ask permission before photographing people",
            "Many spots get crowded during holidays - visit on weekdays for better shots"
        ]
    }


def _get_photography_tips(destination_name: str, category: str) -> List[str]:
    """Generate specific photography tips for each destination."""
    tips_map = {
        "Hồ Xuân Hương": ["Visit at sunrise for misty lake shots", "Capture swan boats for romantic compositions"],
        "Lang Biang Mountain": ["Use wide-angle lens for panoramic views", "Morning fog creates dramatic atmosphere"],
        "Thung Lũng Tình Yêu (Valley of Love)": ["Afternoon light enhances flower colors", "Use props and installations creatively"],
        "The Florest": ["Soft natural lighting ideal for portraits", "Focus on floral details and architecture"],
        "God Valley (Thung Lũng Vàng)": ["Golden hour is essential", "Bring wide-angle lens for landscape shots"],
        "Crazy House (Hằng Nga Villa)": ["Explore different angles and levels", "Early morning avoids crowds"],
        "Datanla Waterfall": ["Use slow shutter for silky water effect", "Bring waterproof protection"],
        "Linh Phước Pagoda": ["Capture mosaic details up close", "Colorful dragon sculpture is main feature"]
    }
    
    default_tips = [
        f"Great for {category} destination photography",
        "Arrive early to avoid crowds"
    ]
    
    return tips_map.get(destination_name, default_tips)

