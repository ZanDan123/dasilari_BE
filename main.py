from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError
import traceback

from app.database import engine, Base
from app.routes import users_router, destinations_router, chat_router, itineraries_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for startup and shutdown events.
    Creates database tables on startup.
    """
    # Startup: Create database tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    
    yield
    
    # Shutdown: cleanup if needed
    print("Shutting down application...")


# Initialize FastAPI app with custom documentation
app = FastAPI(
    title="DasiLari - Da Lat Travel Assistant",
    description="""
    🌸 **DasiLari** is an AI-powered travel assistant for exploring Da Lat, Vietnam.
    
    ## Features
    
    * **Smart Chat Assistant** - Chat with AI to get personalized travel recommendations
    * **Emotion-Based Suggestions** - Get destination recommendations based on your mood
    * **Personalized Itineraries** - Generate complete day plans with time, cost, and directions
    * **Travel Matching** - Find travel buddies with similar preferences
    * **Photo Spots** - Discover Instagram-worthy locations across Da Lat
    * **Destination Database** - 20+ curated Da Lat attractions with detailed information
    
    ## User Journey
    
    1. **Complete Survey** (`POST /api/survey`) - Share your travel preferences
    2. **Chat with AI** (`POST /api/chat`) - Get personalized recommendations
    3. **Generate Itinerary** (`POST /api/itineraries/generate`) - Create your perfect day plan
    4. **Explore Destinations** (`GET /api/destinations`) - Browse all available locations
    5. **Find Photo Spots** (`GET /api/destinations/photo-spots`) - Discover photogenic locations
    
    ## Technology Stack
    
    - **FastAPI** - Modern Python web framework
    - **Google Gemini 1.5 Flash** - AI-powered chat and recommendations
    - **PostgreSQL** - Reliable data storage
    - **SQLAlchemy** - Database ORM
    
    ## Getting Started
    
    1. Seed destinations: `POST /api/destinations/seed`
    2. Create user profile: `POST /api/survey`
    3. Start chatting: `POST /api/chat`
    
    ---
    
    Made with ❤️ for Da Lat travelers
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Configure CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React default
        "http://localhost:5173",  # Vite default
        "http://localhost:8080",  # Vue default
        "http://localhost:4200",  # Angular default
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:4200",
        "https://*.vercel.app",  # All Vercel subdomains
        # Add your specific production frontend URL here after deployment
        # Example: "https://dasilari-frontend.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Error Handling Middleware

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors with detailed error messages.
    Returns 422 status code with validation details.
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Invalid input data. Please check your request.",
            "details": errors
        }
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Handle database errors (connection, query, integrity errors).
    Returns 500 status code for general errors, 409 for integrity violations.
    """
    # Check if it's an integrity error (duplicate, foreign key violation, etc.)
    if isinstance(exc, IntegrityError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "Database Integrity Error",
                "message": "The operation conflicts with existing data. This might be a duplicate entry or invalid reference.",
                "details": str(exc.orig) if hasattr(exc, 'orig') else str(exc)
            }
        )
    
    # General database error
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Database Error",
            "message": "A database error occurred. Please try again later.",
            "details": "Database connection or query error. Check server logs for details."
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Catch-all handler for unexpected errors.
    Handles AI API errors, network errors, and other exceptions.
    """
    # Check if it's an OpenAI API error
    error_message = str(exc)
    
    if "gemini" in error_message.lower() or "google" in error_message.lower() or "api" in error_message.lower():
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "AI Service Error",
                "message": "The AI service is temporarily unavailable. Please try again.",
                "details": "Gemini API error. Check your API key and quota.",
                "fallback": "You can still browse destinations and create manual itineraries."
            }
        )
    
    # Check for environment/configuration errors
    if "environment" in error_message.lower() or "GEMINI_API_KEY" in error_message:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Configuration Error",
                "message": "Server configuration error. Please contact administrator.",
                "details": "Missing or invalid environment variables."
            }
        )
    
    # Log the full error for debugging
    print(f"Unexpected error: {exc}")
    print(traceback.format_exc())
    
    # Generic error response
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Our team has been notified.",
            "details": str(exc) if app.debug else "Please try again later or contact support."
        }
    )


# Include all routers
app.include_router(users_router)
app.include_router(destinations_router)
app.include_router(chat_router)
app.include_router(itineraries_router)


# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint to verify the API is running.
    Returns status and version information.
    """
    return {
        "status": "healthy",
        "service": "DasiLari API",
        "version": "1.0.0",
        "message": "Da Lat Travel Assistant is running smoothly!"
    }


# Root endpoint
@app.get("/", tags=["Root"])
def root():
    """
    Root endpoint with welcome message and quick links.
    """
    return {
        "message": "Welcome to DasiLari - Your Da Lat Travel Assistant! 🌸",
        "description": "AI-powered travel assistant for exploring Da Lat, Vietnam",
        "documentation": "/docs",
        "health_check": "/health",
        "endpoints": {
            "survey": "POST /api/survey - Submit user preferences",
            "chat": "POST /api/chat - Chat with AI assistant",
            "destinations": "GET /api/destinations - Browse destinations",
            "photo_spots": "GET /api/destinations/photo-spots - Find photo spots",
            "generate_itinerary": "POST /api/itineraries/generate - Create itinerary",
            "user_itineraries": "GET /api/itineraries/{user_id} - View saved itineraries"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🌸 DasiLari - Da Lat Travel Assistant 🌸               ║
    ║                                                           ║
    ║   Starting server...                                      ║
    ║   API Documentation: http://localhost:8000/docs           ║
    ║   Health Check: http://localhost:8000/health              ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
