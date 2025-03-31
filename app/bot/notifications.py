from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from app.bot.config import settings
from app.db.models import TravelRequest
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

async def send_request_notification(bot, request_data: dict, admin_ids: list):
    """Отправляет уведомление администратору о новой заявке"""
    try:
        status_emoji = {
            "pending": "⏳",
            "approved": "✅",
            "rejected": "❌",
            "cancelled": "🚫"
        }.get(request_data.get('status', 'pending'), "❓")

        # Преобразуем время создания в UTC+3
        created_at = datetime.fromisoformat(request_data.get('created_at', '').replace('Z', '+00:00'))
        created_at = created_at + timedelta(hours=3)

        message = (
            f"🆕 Новая заявка!\n\n"
            f"ID: {request_data.get('id')}\n"
            f"Тур: {request_data.get('tour', {}).get('title', 'Не указан')}\n"
            f"Статус: {status_emoji} {request_data.get('status', 'pending')}\n"
            f"Дата создания: {created_at.strftime('%d.%m.%Y %H:%M')} (UTC+3)\n\n"
        )

        if request_data.get('user'):
            message += f"Пользователь: {request_data['user'].get('username', 'Не указан')}\n"
        else:
            message += (
                f"Гость:\n"
                f"Имя: {request_data.get('guest_name', 'Не указано')}\n"
                f"Email: {request_data.get('guest_email', 'Не указано')}\n"
                f"Телефон: {request_data.get('guest_phone', 'Не указано')}\n"
            )

        if request_data.get('comment'):
            message += f"\nКомментарий: {request_data['comment']}"

        # Добавляем кнопки для быстрого управления статусом
        keyboard = []
        for new_status in ["approved", "rejected", "cancelled"]:
            keyboard.append([
                InlineKeyboardButton(
                    f"Установить статус: {new_status}",
                    callback_data=f"status_{request_data['id']}_{new_status}"
                )
            ])
        keyboard.append([InlineKeyboardButton("📝 Все заявки", callback_data="admin_requests")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Отправляем уведомление всем администраторам
        for admin_id in admin_ids:
            try:
                # Проверяем, существует ли чат
                try:
                    chat = await bot.get_chat(admin_id)
                    if chat:
                        try:
                            await bot.send_message(
                                chat_id=admin_id,
                                text=message,
                                reply_markup=reply_markup
                            )
                        except Exception as e:
                            logger.error(f"Error sending message to admin {admin_id}: {e}")
                            # Пробуем отправить сообщение без кнопок
                            try:
                                await bot.send_message(
                                    chat_id=admin_id,
                                    text=message
                                )
                            except Exception as e2:
                                logger.error(f"Error sending plain message to admin {admin_id}: {e2}")
                except Exception as e:
                    logger.error(f"Error checking chat for admin {admin_id}: {e}")
                    continue
            except Exception as e:
                logger.error(f"Error processing admin {admin_id}: {e}")

    except Exception as e:
        logger.error(f"Error in send_request_notification: {e}")

async def send_group_notification(request: TravelRequest):
    """Отправка уведомления о новой заявке администратору"""
    try:
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        
        # Формируем сообщение
        message = "🆕 Новая заявка на тур!\n\n"
        message += f"ID заявки: {request.id}\n"
        message += f"Тур: {request.tour.title}\n"
        # Добавляем 3 часа к времени
        created_at = request.created_at + timedelta(hours=3)
        message += f"Дата: {created_at.strftime('%d.%m.%Y %H:%M')} (UTC+3)\n\n"
        
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
        
        # Добавляем кнопки для быстрого управления статусом
        keyboard = []
        for new_status in ["approved", "rejected", "cancelled"]:
            keyboard.append([
                InlineKeyboardButton(
                    f"Установить статус: {new_status}",
                    callback_data=f"status_{request.id}_{new_status}"
                )
            ])
        keyboard.append([InlineKeyboardButton("📝 Все заявки", callback_data="admin_requests")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправляем уведомление администратору
        admin_id = 1448953141  # Ваш ID
        try:
            logger.info(f"Attempting to send message to admin {admin_id}")
            
            # Пробуем отправить сообщение с кнопками
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=message,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
                logger.info(f"Successfully sent message to admin {admin_id}")
            except Exception as e:
                logger.error(f"Error sending message with buttons to admin {admin_id}: {e}")
                # Если не удалось отправить сообщение с кнопками, пробуем без них
                try:
                    await bot.send_message(
                        chat_id=admin_id,
                        text=message,
                        parse_mode='HTML'
                    )
                    logger.info(f"Successfully sent plain message to admin {admin_id}")
                except Exception as e2:
                    logger.error(f"Error sending plain message to admin {admin_id}: {e2}")
                    
        except Exception as e:
            logger.error(f"Error in admin notification: {e}")
            
    except Exception as e:
        logger.error(f"Error in send_group_notification: {e}") 