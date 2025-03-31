from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Table, ARRAY
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    travel_requests = relationship("TravelRequest", back_populates="user")

class Tour(Base):
    __tablename__ = "tours"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    duration = Column(Integer)
    image_url = Column(String)
    location = Column(String)
    rating = Column(Float, default=0.0)
    max_participants = Column(Integer)
    available_spots = Column(Integer)
    is_hot = Column(Boolean, default=False)
    departure_date = Column(DateTime, nullable=True)
    return_date = Column(DateTime, nullable=True)
    available_dates = Column(ARRAY(DateTime))  # Changed to ARRAY type
    created_at = Column(DateTime, default=datetime.utcnow)

    travel_requests = relationship("TravelRequest", back_populates="tour")

class TravelRequest(Base):
    __tablename__ = "travel_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tour_id = Column(Integer, ForeignKey("tours.id"))
    status = Column(String)  # pending, confirmed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="travel_requests")
    tour = relationship("Tour", back_populates="travel_requests") 