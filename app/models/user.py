from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    personality_type = Column(String, nullable=False)  # extrovert/introvert
    travel_style = Column(String, nullable=False)  # group/solo
    transport_type = Column(String, nullable=False)
    has_itinerary = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
