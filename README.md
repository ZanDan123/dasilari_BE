# DasiLari - Da Lat Travel Assistant 🌸

AI-powered travel assistant for exploring Da Lat, Vietnam. Get personalized destination recommendations, emotion-based suggestions, and complete itinerary planning.

## Features

- 🤖 **AI Chat Assistant** - Powered by Google Gemini 1.5 Flash for intelligent travel advice
- 😊 **Emotion Detection** - Get destination suggestions based on your mood
- 📅 **Smart Itineraries** - Auto-generated day plans with costs and directions
- 📸 **Photo Spots** - Discover 18+ Instagram-worthy locations
- 👥 **Travel Matching** - Find companions with similar preferences
- 🗺️ **20+ Destinations** - Curated Da Lat attractions with detailed information

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create `.env` file with your credentials:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/dasilari
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Run the Server

```bash
# Start the FastAPI server
python main.py

# Or use uvicorn directly
uvicorn main:app --reload
```

Server runs at: http://localhost:8000  
API Documentation: http://localhost:8000/docs

## API Examples

### 1. Seed Database with Destinations

```bash
curl -X POST http://localhost:8000/api/destinations/seed \
  -H "Content-Type: application/json"
```

**Response:**

```json
{
  "message": "Successfully seeded 20 Da Lat destinations",
  "count": 20,
  "status": "success"
}
```

---

### 2. Submit User Survey

Create your travel profile with preferences.

```bash
curl -X POST http://localhost:8000/api/survey \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Nguyen",
    "personality_type": "extrovert",
    "travel_style": "group",
    "transport_type": "motorbike",
    "has_itinerary": false
  }'
```

**Response:**

```json
{
  "user_id": 1,
  "message": "Survey data saved successfully",
  "status": "success"
}
```

**Personality Types:** `extrovert`, `introvert`  
**Travel Styles:** `group`, `solo`

---

### 3. Chat with AI Assistant

Get personalized travel recommendations through conversation.

**Example 1: General Question**

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to visit romantic places in Da Lat",
    "user_id": 1
  }'
```

**Response:**

```json
{
  "response": "Da Lat is perfect for romance! I recommend starting with...",
  "suggested_destinations": [
    {
      "id": 3,
      "name": "Thung Lũng Tình Yêu (Valley of Love)",
      "location": "5km north of Da Lat",
      "reason": "Perfect romantic valley with gardens and lakes",
      "priority": "high",
      "cost": 50000.0,
      "time": 120,
      "photo_spot": true
    }
  ],
  "metadata": {
    "detected_emotion": "romantic",
    "detected_intents": ["destination_suggestion"],
    "user_personality": "extrovert",
    "user_travel_style": "group"
  }
}
```

**Example 2: Emotion-Based Request**

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I am feeling stressed and need to relax",
    "user_id": 1
  }'
```

**Example 3: Photo Spots Request**

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Where can I take good Instagram photos?",
    "user_id": 1
  }'
```

---

### 4. Search Destinations

Browse all destinations with filters.

**Get All Destinations:**

```bash
curl -X GET http://localhost:8000/api/destinations
```

**Filter by Category:**

```bash
# Get famous destinations
curl -X GET "http://localhost:8000/api/destinations?category=famous"

# Get local hidden gems
curl -X GET "http://localhost:8000/api/destinations?category=local"
```

**Filter by Photo Spots:**

```bash
curl -X GET "http://localhost:8000/api/destinations?photo_spot=true"
```

**Filter by Budget:**

```bash
# Get free or cheap destinations (max 50,000 VND)
curl -X GET "http://localhost:8000/api/destinations?max_cost=50000"
```

**Combine Filters:**

```bash
curl -X GET "http://localhost:8000/api/destinations?category=local&photo_spot=true&max_cost=100000"
```

---

### 5. Get Photo Spots with Tips

Get all photogenic locations with photography advice.

```bash
curl -X GET http://localhost:8000/api/destinations/photo-spots
```

**Response:**

```json
{
  "total_photo_spots": 18,
  "photo_spots": [
    {
      "id": 1,
      "name": "Hồ Xuân Hương",
      "location": "Center of Da Lat",
      "category": "famous",
      "estimated_cost": 0.0,
      "estimated_time": 90,
      "description": "Beautiful lake in the heart of Da Lat...",
      "photogenic_features": "Serene lake reflections, swan boats, and pine trees create picture-perfect scenes",
      "photography_tips": [
        "Visit at sunrise for misty lake shots",
        "Capture swan boats for romantic compositions"
      ]
    }
  ],
  "general_tips": [
    "Best lighting: Early morning (6-8 AM) or golden hour (4-6 PM)",
    "Da Lat weather can change quickly - bring protective gear for your camera"
  ]
}
```

---

### 6. Generate Itinerary

Create a complete day plan with AI.

```bash
curl -X POST http://localhost:8000/api/itineraries/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "destination_ids": [1, 2, 3, 4],
    "visit_date": "2025-12-28",
    "emotion": "excited"
  }'
```

**Response:**

```json
{
  "status": "success",
  "message": "Itinerary generated and saved successfully",
  "user_id": 1,
  "visit_date": "2025-12-28",
  "emotion_tag": "excited",
  "itinerary": {
    "title": "Your Da Lat Day Trip",
    "total_estimated_cost": 270000,
    "total_duration": "8 hours",
    "schedule": [
      {
        "destination_id": 1,
        "destination_name": "Hồ Xuân Hương",
        "time_slot": "morning",
        "time_range": "08:00 - 10:00",
        "activity": "Morning walk around the lake",
        "duration": "90 minutes",
        "cost": 0,
        "directions": "Located at Center of Da Lat",
        "tips": "Best time for photos with morning mist"
      }
    ],
    "meal_suggestions": [
      {
        "time": "12:00",
        "suggestion": "Try local bánh mì at Da Lat Market",
        "estimated_cost": 50000
      }
    ]
  },
  "destinations_count": 4
}
```

---

### 7. Get User's Itineraries

Retrieve all saved itineraries with cost calculations.

**Get All Itineraries:**

```bash
curl -X GET http://localhost:8000/api/itineraries/1
```

**Filter by Date:**

```bash
curl -X GET "http://localhost:8000/api/itineraries/1?visit_date=2025-12-28"
```

**Response:**

```json
{
  "user_id": 1,
  "user_name": "Alice Nguyen",
  "user_preferences": {
    "personality_type": "extrovert",
    "travel_style": "group",
    "transport_type": "motorbike"
  },
  "itineraries": [
    {
      "visit_date": "2025-12-28",
      "emotion_tag": "excited",
      "destinations": [
        {
          "itinerary_id": 1,
          "destination": {
            "id": 1,
            "name": "Hồ Xuân Hương",
            "location": "Center of Da Lat",
            "category": "famous",
            "photo_spot": true,
            "estimated_cost": 0.0,
            "estimated_time": 90
          },
          "time_slot": "morning"
        }
      ],
      "total_cost": 270000,
      "total_time": 540
    }
  ],
  "summary": {
    "total_itineraries": 1,
    "total_destinations": 4,
    "total_cost": 270000,
    "average_cost_per_day": 270000
  }
}
```

---

### 8. Get User Profile

```bash
curl -X GET http://localhost:8000/api/users/1
```

---

### 9. Health Check

```bash
curl -X GET http://localhost:8000/health
```

**Response:**

```json
{
  "status": "healthy",
  "service": "DasiLari API",
  "version": "1.0.0",
  "message": "Da Lat Travel Assistant is running smoothly!"
}
```

## Project Structure

```
DasiLari/
├── app/
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── database.py          # Database configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py              # User model
│   │   ├── destination.py       # Destination model
│   │   └── itinerary.py         # Itinerary model
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── users.py             # User endpoints
│   │   ├── destinations.py      # Destination endpoints
│   │   ├── chat.py              # Chat endpoints
│   │   └── itineraries.py       # Itinerary endpoints
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py              # User Pydantic schemas
│   │   ├── destination.py       # Destination schemas
│   │   └── chat.py              # Chat schemas
│   └── services/
│       ├── __init__.py
│       ├── ai_service.py        # OpenAI integration
│       └── matching.py          # Travel matching service
├── main.py                      # FastAPI application
├── requirements.txt             # Dependencies
├── .env                         # Environment variables
└── README.md                    # This file
```

## Database Models

### User

- Stores personality type (extrovert/introvert)
- Travel style (group/solo)
- Transport preferences
- Itinerary status

### Destination

- 20+ Da Lat locations
- Cost and time estimates
- Category (local/famous)
- Photo spot indicators

### Itinerary

- Links users to destinations
- Time slots (morning/afternoon/evening)
- Visit dates
- Emotion tags

## Technologies

- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **PostgreSQL** - Database
- **Google Gemini 1.5 Flash** - AI chat and recommendations
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

## Environment Variables

| Variable         | Description                  | Required |
| ---------------- | ---------------------------- | -------- |
| `DATABASE_URL`   | PostgreSQL connection string | Yes      |
| `OPENAI_API_KEY` | OpenAI API key for GPT-3.5   | Yes      |

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Error Codes

| Status Code | Description                        |
| ----------- | ---------------------------------- |
| 200         | Success                            |
| 201         | Created                            |
| 400         | Bad Request - Invalid input        |
| 404         | Not Found - Resource doesn't exist |
| 500         | Internal Server Error              |

## Development

```bash
# Run with auto-reload
uvicorn main:app --reload --port 8000

# Run tests (if implemented)
pytest

# Format code
black .

# Check types
mypy .
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

MIT License - feel free to use this project for your own Da Lat adventures!

## Support

For issues or questions:

- Open an issue on GitHub
- Check API documentation at `/docs`
- Review error messages in responses

---

**Made with ❤️ for Da Lat travelers**
