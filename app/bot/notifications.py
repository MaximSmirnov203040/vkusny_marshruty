from telegram import Bot
from app.bot.config import settings
from app.db.models import TravelRequest
from datetime import datetime

async def send_request_notification(request: TravelRequest):
    """Отправка уведомления о новой заявке в группу"""
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    
    # Формируем сообщение
    message = "🆕 Новая заявка на тур!\n\n"
    message += f"Тур: {request.tour.title}\n"
    message += f"Дата: {request.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
    
    if request.user_id:
        message += f"Пользователь: {request.user.username}\n"
    else:
        message += (
            f"Гость: {request.guest_name}\n"
            f"Email: {request.guest_email}\n"
            f"Телефон: {request.guest_phone}\n"
        )
    
    if request.comment:
        message += f"\nКомментарий: {request.comment}"
    
    # Отправляем сообщение в группу
    await bot.send_message(
        chat_id=settings.TELEGRAM_GROUP_ID,
        text=message,
        parse_mode='HTML'
    ) 