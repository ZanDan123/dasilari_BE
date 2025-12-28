from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.models.destination import Destination
from app.schemas.destination import DestinationCreate, DestinationResponse

router = APIRouter(prefix="/api/destinations", tags=["destinations"])


@router.get("", response_model=List[DestinationResponse])
def get_destinations(
    category: Optional[str] = Query(None, description="Filter by category: local or famous"),
    photo_spot: Optional[bool] = Query(None, description="Filter by photo spot availability"),
    max_cost: Optional[float] = Query(None, description="Filter by maximum cost", ge=0),
    db: Session = Depends(get_db)
):
    """
    List all Da Lat destinations with optional filters.
    
    Filters:
    - category: Filter by 'local' or 'famous' destinations
    - photo_spot: Filter destinations that are photo spots (true/false)
    - max_cost: Filter destinations with cost less than or equal to specified amount
    """
    query = db.query(Destination)
    
    # Apply filters
    if category:
        query = query.filter(Destination.category == category)
    
    if photo_spot is not None:
        query = query.filter(Destination.photo_spot == photo_spot)
    
    if max_cost is not None:
        query = query.filter(Destination.estimated_cost <= max_cost)
    
    destinations = query.all()
    return destinations


@router.get("/photo-spots")
def get_photo_spots(db: Session = Depends(get_db)):
    """
    Get all destinations that are great photo spots with descriptions of why they are photogenic.
    Perfect for Instagram-worthy locations and photography enthusiasts.
    
    Returns destinations with photo_spot=True, including details about their visual appeal.
    """
    photo_destinations = db.query(Destination).filter(
        Destination.photo_spot == True
    ).all()
    
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
            "id": destination.id,
            "name": destination.name,
            "location": destination.location,
            "category": destination.category,
            "estimated_cost": destination.estimated_cost,
            "estimated_time": destination.estimated_time,
            "description": destination.description,
            "photogenic_features": photo_reasons.get(
                destination.name,
                "Beautiful scenery perfect for photography and creating lasting memories"
            ),
            "photography_tips": _get_photography_tips(destination.name, destination.category)
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


@router.post("/seed", status_code=status.HTTP_201_CREATED)
def seed_destinations(db: Session = Depends(get_db)):
    """
    Populate database with 20 Da Lat destinations including popular spots
    like Hồ Xuân Hương, Lang Biang, Thung Lũng Tình Yêu, The Florest, and God Valley.
    """
    # Check if destinations already exist
    existing_count = db.query(Destination).count()
    if existing_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database already contains {existing_count} destinations. Clear database before seeding."
        )
    
    destinations_data = [
        {
            "name": "Hồ Xuân Hương",
            "location": "Center of Da Lat",
            "category": "famous",
            "photo_spot": True,
            "estimated_cost": 0.0,
            "estimated_time": 90,
            "description": "Beautiful lake in the heart of Da Lat, perfect for walking and swan boat rides. Free entry with stunning views."
        },
        {
            "name": "Lang Biang Mountain",
            "location": "12km north of Da Lat",
            "category": "famous",
            "photo_spot": True,
            "estimated_cost": 70000.0,
            "estimated_time": 240,
            "description": "The highest peak in Da Lat at 2,167m. Jeep tours available or hiking to the summit for panoramic views."
        },
        {
            "name": "Thung Lũng Tình Yêu (Valley of Love)",
            "location": "5km north of Da Lat",
            "category": "famous",
            "photo_spot": True,
            "estimated_cost": 50000.0,
            "estimated_time": 120,
            "description": "Romantic valley with gardens, lakes, and colorful flower displays. Popular for couples and photography."
        },
        {
            "name": "The Florest",
            "location": "Trần Hưng Đạo, Da Lat",
            "category": "local",
            "photo_spot": True,
            "estimated_cost": 50000.0,
            "estimated_time": 90,
            "description": "Instagram-worthy garden café with European-style architecture and beautiful flower arrangements."
        },
        {
            "name": "God Valley (Thung Lũng Vàng)",
            "location": "20km from Da Lat center",
            "category": "local",
            "photo_spot": True,
            "estimated_cost": 100000.0,
            "estimated_time": 180,
            "description": "Hidden gem with golden grass fields, perfect for photography and peaceful nature walks."
        },
        {
            "name": "Crazy House (Hằng Nga Villa)",
            "location": "3 Huỳnh Thúc Kháng, Da Lat",
            "category": "famous",
            "photo_spot": True,
            "estimated_cost": 80000.0,
            "estimated_time": 60,
            "description": "Unique architectural wonder designed by architect Đặng Việt Nga. Surreal fairy-tale structures."
        },
        {
            "name": "Datanla Waterfall",
            "location": "5km south of Da Lat",
            "category": "famous",
            "photo_spot": True,
            "estimated_cost": 50000.0,
            "estimated_time": 120,
            "description": "Popular waterfall with alpine coaster rides and adventure activities. Great for thrill-seekers."
        },
        {
            "name": "Da Lat Night Market",
            "location": "Nguyễn Thị Minh Khai, Da Lat",
            "category": "local",
            "photo_spot": False,
            "estimated_cost": 100000.0,
            "estimated_time": 120,
            "description": "Vibrant night market with local street food, souvenirs, and warm clothing. Best visited after 6 PM."
        },
        {
            "name": "Trúc Lâm Zen Monastery",
            "location": "Phường 3, Da Lat",
            "category": "famous",
            "photo_spot": True,
            "estimated_cost": 0.0,
            "estimated_time": 90,
            "description": "Peaceful Buddhist monastery on Tuyền Lâm Lake. Cable car ride offers stunning views."
        },
        {
            "name": "Da Lat Railway Station",
            "location": "1 Quang Trung, Da Lat",
            "category": "famous",
            "photo_spot": True,
            "estimated_cost": 0.0,
            "estimated_time": 45,
            "description": "Historic French colonial railway station built in 1932. Beautiful architecture and vintage trains."
        },
        {
            "name": "Bảo Đại Summer Palace",
            "location": "Triệu Việt Vương, Da Lat",
            "category": "famous",
            "photo_spot": True,
            "estimated_cost": 30000.0,
            "estimated_time": 60,
            "description": "Former summer residence of Vietnam's last emperor. Art Deco architecture with historical artifacts."
        },
        {
            "name": "XQ Historical Village",
            "location": "01 Huỳnh Thúc Kháng, Da Lat",
            "category": "local",
            "photo_spot": True,
            "estimated_cost": 0.0,
            "estimated_time": 60,
            "description": "Hand-embroidery art gallery showcasing Vietnamese silk art. Free entry with stunning artworks."
        },
        {
            "name": "Linh Phước Pagoda",
            "location": "120 Tự Phước, Trại Mát",
            "category": "famous",
            "photo_spot": True,
            "estimated_cost": 0.0,
            "estimated_time": 45,
            "description": "Stunning pagoda decorated with mosaic glass and ceramic. Features a 49-meter dragon sculpture."
        },
        {
            "name": "Da Lat Flower Gardens",
            "location": "2 Phù Đổng Thiên Vương, Da Lat",
            "category": "famous",
            "photo_spot": True,
            "estimated_cost": 60000.0,
            "estimated_time": 90,
            "description": "Expansive gardens with diverse flower species, topiary, and themed sections. Perfect for flower lovers."
        },
        {
            "name": "Mê Linh Coffee Garden",
            "location": "1A Bùi Thị Xuân, Da Lat",
            "category": "local",
            "photo_spot": True,
            "estimated_cost": 80000.0,
            "estimated_time": 90,
            "description": "Scenic coffee plantation and garden café. Learn about coffee production while enjoying the view."
        },
        {
            "name": "Elephant Falls",
            "location": "30km southwest of Da Lat",
            "category": "famous",
            "photo_spot": True,
            "estimated_cost": 20000.0,
            "estimated_time": 150,
            "description": "Impressive waterfall with powerful cascades. Requires some hiking but worth the adventure."
        },
        {
            "name": "Pongour Waterfall",
            "location": "50km south of Da Lat",
            "category": "local",
            "photo_spot": True,
            "estimated_cost": 20000.0,
            "estimated_time": 180,
            "description": "Majestic seven-tiered waterfall, often called the most beautiful in Da Lat. Best in rainy season."
        },
        {
            "name": "Ana Mandara Villas",
            "location": "Lê Lai, Da Lat",
            "category": "local",
            "photo_spot": True,
            "estimated_cost": 150000.0,
            "estimated_time": 120,
            "description": "French colonial villa complex with restaurants and spa. Experience luxury and history."
        },
        {
            "name": "Clay Tunnel (Hầm Đất Sét)",
            "location": "Lê Hồng Phong, Da Lat",
            "category": "local",
            "photo_spot": True,
            "estimated_cost": 100000.0,
            "estimated_time": 90,
            "description": "Unique clay sculpture tunnel and art space. Creative and quirky attraction perfect for Instagram."
        },
        {
            "name": "Da Lat Market",
            "location": "Nguyễn Thị Minh Khai, Da Lat",
            "category": "local",
            "photo_spot": False,
            "estimated_cost": 50000.0,
            "estimated_time": 90,
            "description": "Traditional market selling fresh produce, flowers, local delicacies, and souvenirs. Authentic local experience."
        }
    ]
    
    try:
        destinations = [Destination(**data) for data in destinations_data]
        db.add_all(destinations)
        db.commit()
        
        return {
            "message": "Successfully seeded 20 Da Lat destinations",
            "count": len(destinations_data),
            "status": "success"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to seed destinations: {str(e)}"
        )
