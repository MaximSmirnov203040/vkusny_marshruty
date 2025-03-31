from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    username: str
    email: EmailStr

    class Config:
        from_attributes = True

class UserCreate(UserBase):
    password: str
    is_admin: bool = False  # Default to False for security

class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

class TourBase(BaseModel):
    title: str
    description: str
    price: float
    duration: int
    image_url: str
    location: str
    rating: float = 0.0
    max_participants: int
    available_spots: int
    is_hot: bool = False
    departure_date: Optional[datetime] = None
    return_date: Optional[datetime] = None
    available_dates: List[datetime] = []

    class Config:
        from_attributes = True

class TourCreate(TourBase):
    pass

class Tour(TourBase):
    id: int
    created_at: datetime

class TravelRequestBase(BaseModel):
    tour_id: int

    class Config:
        from_attributes = True

class GuestTravelRequestCreate(BaseModel):
    tour_id: int
    guest_name: str
    guest_email: EmailStr
    guest_phone: str
    comment: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "tour_id": 1,
                "guest_name": "Иван Иванов",
                "guest_email": "ivan@example.com",
                "guest_phone": "+7 999 123 45 67",
                "comment": "Хотел бы узнать подробнее о туре"
            }
        }

class TravelRequestCreate(TravelRequestBase):
    pass

class TravelRequest(TravelRequestBase):
    id: int
    user_id: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime
    guest_name: Optional[str]
    guest_email: Optional[str]
    guest_phone: Optional[str]
    comment: Optional[str]

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "strongpassword123"
            }
        } 