from sqladmin import ModelView, Admin, BaseView, expose
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.authentication import AuthenticationBackend, AuthCredentials, SimpleUser
from fastapi import FastAPI, Depends, Request, Response
from app.db.models import Tour, User, TravelRequest
from app.db.database import engine
from app.api.endpoints.auth import get_current_user
from sqlalchemy.orm import Session
from app.db.database import get_db
from typing import Optional, List
from app.core.security import verify_password
from datetime import datetime

def format_datetime(value):
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%d.%m.%Y %H:%M")
    return value

def format_price(value):
    if value is None:
        return ""
    return f"{value:,.2f} ₽".replace(",", " ")

class AdminAuth:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.middlewares: List = []

    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form.get("username"), form.get("password")
        
        try:
            db: Session = next(get_db())
            user = db.query(User).filter(User.email == email).first()
            
            if user and user.is_admin and verify_password(password, user.hashed_password):
                request.session["admin-auth"] = email
                return True
        except:
            pass
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        email = request.session.get("admin-auth")
        if not email:
            return False
        
        try:
            db: Session = next(get_db())
            user = db.query(User).filter(User.email == email).first()
            return bool(user and user.is_admin)
        except:
            return False

class TourAdmin(ModelView, model=Tour):
    name = "Тур"
    name_plural = "Туры"
    icon = "fa-solid fa-map"
    column_list = [Tour.id, Tour.title, Tour.price, Tour.duration, Tour.location]
    form_columns = [
        Tour.title,
        Tour.description,
        Tour.price,
        Tour.duration,
        Tour.image_url,
        Tour.location,
        Tour.rating,
        Tour.max_participants,
        Tour.available_spots,
        Tour.is_hot,
        Tour.departure_date,
        Tour.return_date,
        Tour.available_dates
    ]
    column_labels = {
        Tour.id: "ID",
        Tour.title: "Название",
        Tour.price: "Цена",
        Tour.duration: "Длительность",
        Tour.location: "Место",
        Tour.description: "Описание",
        Tour.image_url: "URL изображения",
        Tour.rating: "Рейтинг",
        Tour.max_participants: "Макс. участников",
        Tour.available_spots: "Свободных мест",
        Tour.is_hot: "Горящий тур",
        Tour.departure_date: "Дата отправления",
        Tour.return_date: "Дата возвращения",
        Tour.available_dates: "Доступные даты"
    }
    column_formatters = {
        Tour.is_hot: lambda m, a: "Да" if m.is_hot else "Нет",
        Tour.price: lambda m, a: format_price(m.price),
        Tour.departure_date: lambda m, a: format_datetime(m.departure_date),
        Tour.return_date: lambda m, a: format_datetime(m.return_date),
        Tour.available_dates: lambda m, a: ", ".join(format_datetime(d) for d in m.available_dates) if m.available_dates else "",
        Tour.duration: lambda m, a: f"{m.duration} дней",
        Tour.rating: lambda m, a: f"{m.rating:.1f}" if m.rating else "Нет оценок"
    }

class UserAdmin(ModelView, model=User):
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-users"
    column_list = [User.id, User.username, User.email, User.is_active, User.is_admin]
    form_columns = [
        User.username,
        User.email,
        User.is_active,
        User.is_admin
    ]
    column_labels = {
        User.id: "ID",
        User.username: "Имя пользователя",
        User.email: "Email",
        User.is_active: "Активен",
        User.is_admin: "Администратор",
        User.created_at: "Дата регистрации"
    }
    column_formatters = {
        User.is_active: lambda m, a: "Да" if m.is_active else "Нет",
        User.is_admin: lambda m, a: "Да" if m.is_admin else "Нет",
        User.created_at: lambda m, a: format_datetime(m.created_at)
    }

class TravelRequestAdmin(ModelView, model=TravelRequest):
    name = "Заявка"
    name_plural = "Заявки"
    icon = "fa-solid fa-clipboard-list"
    column_list = [
        TravelRequest.id,
        TravelRequest.user_id,
        TravelRequest.tour_id,
        TravelRequest.guest_name,
        TravelRequest.guest_email,
        TravelRequest.guest_phone,
        TravelRequest.status,
        TravelRequest.created_at
    ]
    form_columns = [
        TravelRequest.user_id,
        TravelRequest.tour_id,
        TravelRequest.guest_name,
        TravelRequest.guest_email,
        TravelRequest.guest_phone,
        TravelRequest.comment,
        TravelRequest.status
    ]
    column_labels = {
        TravelRequest.id: "ID",
        TravelRequest.user_id: "ID пользователя",
        TravelRequest.tour_id: "ID тура",
        TravelRequest.guest_name: "Имя гостя",
        TravelRequest.guest_email: "Email гостя",
        TravelRequest.guest_phone: "Телефон гостя",
        TravelRequest.comment: "Комментарий",
        TravelRequest.status: "Статус",
        TravelRequest.created_at: "Дата создания",
        TravelRequest.updated_at: "Дата обновления"
    }
    column_formatters = {
        TravelRequest.status: lambda m, a: {
            "pending": "В ожидании",
            "approved": "Одобрено",
            "rejected": "Отклонено",
            "cancelled": "Отменено"
        }.get(m.status, m.status),
        TravelRequest.created_at: lambda m, a: format_datetime(m.created_at),
        TravelRequest.updated_at: lambda m, a: format_datetime(m.updated_at)
    }
    form_choices = {
        "status": [
            ("pending", "В ожидании"),
            ("approved", "Одобрено"),
            ("rejected", "Отклонено"),
            ("cancelled", "Отменено")
        ]
    }

def setup_admin(app: FastAPI) -> None:
    admin = Admin(
        app,
        engine,
        title="Админ-панель Вкусных Маршрутов",
        authentication_backend=AdminAuth(secret_key=app.state.secret_key)
    )
    
    admin.add_view(TourAdmin)
    admin.add_view(UserAdmin)
    admin.add_view(TravelRequestAdmin) 