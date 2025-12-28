from sqlalchemy import Column, Integer, String, Boolean, Float, Text
from app.database import Base


class Destination(Base):
    __tablename__ = "destinations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    category = Column(String, nullable=False)  # local/famous
    photo_spot = Column(Boolean, default=False)
    estimated_cost = Column(Float, nullable=True)
    estimated_time = Column(Integer, nullable=True)  # in minutes
    description = Column(Text, nullable=True)
