from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    requests = relationship("TravelRequest", back_populates="user")

class Tour(Base):
    __tablename__ = "tours"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    country = Column(String)
    city = Column(String)
    price = Column(Float)
    original_price = Column(Float)
    departure_date = Column(DateTime)
    return_date = Column(DateTime)
    available_spots = Column(Integer)
    is_hot = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    requests = relationship("TravelRequest", back_populates="tour")

class TravelRequest(Base):
    __tablename__ = "travel_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tour_id = Column(Integer, ForeignKey("tours.id"))
    status = Column(String, default="pending")  # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="requests")
    tour = relationship("Tour", back_populates="requests") 