from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Text, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
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
    available_dates = Column(ARRAY(DateTime), default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    requests = relationship("TravelRequest", back_populates="tour")

class TravelRequest(Base):
    __tablename__ = "travel_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable для гостевых заявок
    tour_id = Column(Integer, ForeignKey("tours.id"))
    status = Column(String, default="pending")  # pending, approved, rejected, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Поля для гостевых заявок
    guest_name = Column(String, nullable=True)
    guest_email = Column(String, nullable=True)
    guest_phone = Column(String, nullable=True)
    comment = Column(Text, nullable=True)
    
    user = relationship("User", back_populates="requests")
    tour = relationship("Tour", back_populates="requests") 