from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TourBase(BaseModel):
    title: str
    description: str
    country: str
    city: str
    price: float
    original_price: float
    departure_date: datetime
    return_date: datetime
    available_spots: int
    is_hot: bool = False

class TourCreate(TourBase):
    pass

class Tour(TourBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TravelRequestBase(BaseModel):
    tour_id: int

class TravelRequestCreate(TravelRequestBase):
    pass

class TravelRequest(TravelRequestBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    user: User
    tour: Tour

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None 