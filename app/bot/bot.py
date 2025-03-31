from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db import models
from app.schemas import schemas
from datetime import datetime
from app.bot.config import settings
import logging
import httpx

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

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

class Bot:
    def __init__(self):
        self.application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        self.settings = settings
        self.setup_handlers()

    def is_admin(self, user_id: int) -> bool:
        """Проверка, является ли пользователь администратором"""
        logger.info(f"Checking admin rights for user_id: {user_id}")
        logger.info(f"Admin IDs from settings: {self.settings.ADMIN_IDS}")
        is_admin = user_id in self.settings.ADMIN_IDS
        logger.info(f"Is admin: {is_admin}")
        return is_admin

    def setup_handlers(self):
        """Настраивает обработчики команд"""
        # Команды
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("admin", self.admin_panel))

        # Обработчики callback-запросов
        self.application.add_handler(CallbackQueryHandler(self.handle_callback, pattern="^admin_panel$"))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback, pattern="^list_tours$"))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback, pattern="^list_requests$"))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback, pattern="^create_tour$"))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback, pattern="^help$"))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback, pattern="^admin_tours$"))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback, pattern="^admin_requests$"))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback, pattern="^main_menu$"))
        self.application.add_handler(CallbackQueryHandler(self.handle_request_status, pattern="^status_\d+_[a-zA-Z]+$"))

        # Обработчик текстовых сообщений
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        if update.effective_user.id not in settings.ADMIN_IDS:
            await update.message.reply_text(
                "Этот бот предназначен только для администраторов. "
                "Пожалуйста, обратитесь к администратору для получения доступа."
            )
            return

        keyboard = [
            [InlineKeyboardButton("📋 Список туров", callback_data="admin_tours")],
            [InlineKeyboardButton("👥 Заявки", callback_data="admin_requests")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Добро пожаловать в бот администратора Вкусных Маршрутов!\n"
            "Используйте /help для просмотра доступных команд.",
            reply_markup=reply_markup
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        if update.effective_user.id not in settings.ADMIN_IDS:
            await update.message.reply_text(
                "Этот бот предназначен только для администраторов. "
                "Пожалуйста, обратитесь к администратору для получения доступа."
            )
            return

        help_text = (
            "Доступные команды:\n"
            "/start - Начать работу с ботом\n"
            "/help - Показать это сообщение\n"
            "/admin - Открыть панель администратора\n\n"
            "Для работы с заявками используйте кнопки в меню."
        )
        await update.message.reply_text(help_text)

    async def admin_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает панель администратора"""
        keyboard = [
            [InlineKeyboardButton("📋 Список туров", callback_data="list_tours")],
            [InlineKeyboardButton("➕ Создать тур", callback_data="create_tour")],
            [InlineKeyboardButton("📝 Список заявок", callback_data="list_requests")],
            [InlineKeyboardButton("❓ Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Определяем, откуда пришел запрос
        if update.callback_query:
            message = update.callback_query.message
        else:
            message = update.message

        # Если есть предыдущее сообщение бота, обновляем его
        if 'admin_message_id' in context.user_data:
            try:
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=context.user_data['admin_message_id'],
                    text="🔧 Панель администратора\n\nВыберите действие:",
                    reply_markup=reply_markup
                )
            except Exception as e:
                logging.error(f"Error updating admin panel: {e}")
                # Если не удалось обновить, создаем новое сообщение
                sent_message = await message.reply_text(
                    "🔧 Панель администратора\n\nВыберите действие:",
                    reply_markup=reply_markup
                )
                context.user_data['admin_message_id'] = sent_message.message_id
        else:
            # Создаем новое сообщение
            sent_message = await message.reply_text(
                "🔧 Панель администратора\n\nВыберите действие:",
                reply_markup=reply_markup
            )
            context.user_data['admin_message_id'] = sent_message.message_id

    async def list_tours(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает список всех туров"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.settings.API_URL}/api/v1/tours/",
                    headers={"Authorization": f"Bearer {self.settings.API_TOKEN}"}
                )
                tours = response.json()

            if not tours:
                text = "📋 Список туров пуст"
            else:
                text = "📋 Список всех туров:\n\n"
                for tour in tours:
                    text += (
                        f"🏷 {tour['title']}\n"
                        f"💰 Цена: {tour['price']} руб.\n"
                        f"⏱ Длительность: {tour['duration']} дней\n"
                        f"📍 Место: {tour['location']}\n"
                        f"👥 Мест: {tour['available_spots']}/{tour['max_participants']}\n"
                        f"📅 Отправление: {tour['departure_date']}\n"
                        f"🔄 Возвращение: {tour['return_date']}\n\n"
                    )

            keyboard = [
                [InlineKeyboardButton("🔄 Обновить", callback_data="list_tours")],
                [InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Если есть предыдущее сообщение, обновляем его
            if 'tours_message_id' in context.user_data:
                try:
                    await context.bot.edit_message_text(
                        chat_id=update.effective_chat.id,
                        message_id=context.user_data['tours_message_id'],
                        text=text,
                        reply_markup=reply_markup
                    )
                except Exception as e:
                    logging.error(f"Error updating tours list: {e}")
                    # Если не удалось обновить, создаем новое сообщение
                    message = await update.callback_query.message.reply_text(
                        text,
                        reply_markup=reply_markup
                    )
                    context.user_data['tours_message_id'] = message.message_id
            else:
                # Создаем новое сообщение
                message = await update.callback_query.message.reply_text(
                    text,
                    reply_markup=reply_markup
                )
                context.user_data['tours_message_id'] = message.message_id

        except Exception as e:
            logging.error(f"Error in list_tours: {e}")
            await update.callback_query.message.reply_text(
                "❌ Ошибка при получении списка туров"
            )

    async def list_requests(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать список заявок"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.settings.API_URL}/api/v1/requests/",
                    headers={"Authorization": f"Bearer {self.settings.API_TOKEN}"}
                )
                response.raise_for_status()
                requests = response.json()

            if not requests:
                text = "📝 Список заявок пуст"
            else:
                text = "📝 Список заявок:\n\n"
                for request in requests:
                    text += f"ID: {request['id']}\n"
                    text += f"Тур: {request.get('tour', {}).get('title', 'Не указан')}\n"
                    text += f"Статус: {request.get('status', 'Не указан')}\n"
                    
                    if request.get('user'):
                        text += f"Пользователь: {request['user'].get('username', 'Не указан')}\n"
                    else:
                        text += (
                            f"Гость: {request.get('guest_name', 'Не указано')}\n"
                            f"Email: {request.get('guest_email', 'Не указано')}\n"
                            f"Телефон: {request.get('guest_phone', 'Не указано')}\n"
                        )
                    
                    text += f"Дата создания: {request.get('created_at', 'Не указана')}\n"
                    text += "-------------------\n"

            keyboard = [
                [InlineKeyboardButton("🔄 Обновить", callback_data="list_requests")],
                [InlineKeyboardButton("◀️ Назад", callback_data="admin_panel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Проверяем, есть ли предыдущее сообщение от бота
            if "last_bot_message_id" in context.user_data:
                try:
                    await context.bot.edit_message_text(
                        chat_id=update.effective_chat.id,
                        message_id=context.user_data["last_bot_message_id"],
                        text=text,
                        reply_markup=reply_markup
                    )
                except Exception:
                    # Если не удалось обновить, отправляем новое сообщение
                    message = await update.effective_message.reply_text(
                        text=text,
                        reply_markup=reply_markup
                    )
                    context.user_data["last_bot_message_id"] = message.message_id
            else:
                # Если нет предыдущего сообщения, отправляем новое
                message = await update.effective_message.reply_text(
                    text=text,
                    reply_markup=reply_markup
                )
                context.user_data["last_bot_message_id"] = message.message_id

        except Exception as e:
            logger.error(f"Error listing requests: {e}")
            await update.effective_message.reply_text(
                "❌ Произошла ошибка при получении списка заявок"
            )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        if update.effective_user.id not in settings.ADMIN_IDS:
            await update.message.reply_text(
                "Этот бот предназначен только для администраторов. "
                "Пожалуйста, обратитесь к администратору для получения доступа."
            )
            return

        # Удаляем сообщение пользователя
        try:
            await update.message.delete()
        except Exception as e:
            logging.error(f"Error deleting user message: {e}")

        # Проверяем, создается ли тур
        if context.user_data.get('creating_tour'):
            try:
                logging.info(f"Получены данные для создания тура: {update.message.text}")
                
                # Разбиваем текст на строки
                lines = update.message.text.split('\n')
                logging.info(f"Разбито на {len(lines)} строк")
                
                if len(lines) < 10:
                    raise ValueError(f"Недостаточно данных. Получено {len(lines)} строк, требуется 10")

                # Парсим данные
                title = lines[0].strip()
                description = lines[1].strip()
                price = float(lines[2].strip())
                duration = int(lines[3].strip())
                image_url = lines[4].strip()
                location = lines[5].strip()
                max_participants = int(lines[6].strip())
                available_spots = int(lines[7].strip())
                departure_date = datetime.strptime(lines[8].strip(), "%Y-%m-%d")
                return_date = datetime.strptime(lines[9].strip(), "%Y-%m-%d")

                logging.info(f"Парсинг данных успешен:")
                logging.info(f"Название: {title}")
                logging.info(f"Цена: {price}")
                logging.info(f"Длительность: {duration}")
                logging.info(f"Место: {location}")
                logging.info(f"Макс. участников: {max_participants}")
                logging.info(f"Свободных мест: {available_spots}")
                logging.info(f"Дата отправления: {departure_date}")
                logging.info(f"Дата возвращения: {return_date}")

                # Создаем тур через API
                tour_data = {
                    "title": title,
                    "description": description,
                    "price": price,
                    "duration": duration,
                    "image_url": image_url,
                    "location": location,
                    "max_participants": max_participants,
                    "available_spots": available_spots,
                    "departure_date": departure_date.isoformat(),
                    "return_date": return_date.isoformat()
                }

                logging.info(f"Отправка запроса на {self.settings.API_URL}/api/v1/tours/")
                logging.info(f"Данные тура: {tour_data}")
                logging.info(f"API Token: {self.settings.API_TOKEN}")

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.settings.API_URL}/api/v1/tours/",
                        json=tour_data,
                        headers={"Authorization": f"Bearer {self.settings.API_TOKEN}"}
                    )

                logging.info(f"Ответ API: {response.status_code}")
                logging.info(f"Тело ответа: {response.text}")

                if response.status_code == 200:
                    # Если есть предыдущее сообщение о создании тура, обновляем его
                    if 'create_tour_message_id' in context.user_data:
                        try:
                            await context.bot.edit_message_text(
                                chat_id=update.effective_chat.id,
                                message_id=context.user_data['create_tour_message_id'],
                                text="✅ Тур успешно создан!\n\n"
                                    f"Название: {title}\n"
                                    f"Цена: {price} руб.\n"
                                    f"Длительность: {duration} дней\n"
                                    f"Место: {location}"
                            )
                        except Exception as e:
                            logging.error(f"Error updating create tour message: {e}")
                    else:
                        message = await update.message.reply_text(
                            "✅ Тур успешно создан!\n\n"
                            f"Название: {title}\n"
                            f"Цена: {price} руб.\n"
                            f"Длительность: {duration} дней\n"
                            f"Место: {location}"
                        )
                        context.user_data['create_tour_message_id'] = message.message_id
                else:
                    error_message = f"❌ Ошибка при создании тура. Статус: {response.status_code}\nОтвет: {response.text}"
                    logging.error(error_message)
                    await update.message.reply_text(error_message)

            except Exception as e:
                error_message = f"❌ Ошибка при создании тура: {str(e)}"
                logging.error(error_message, exc_info=True)
                await update.message.reply_text(error_message)

            finally:
                context.user_data['creating_tour'] = False
                # Возвращаемся в админ-панель
                await self.admin_panel(update, context)
                return

        # Если не создается тур, показываем меню администратора
        await self.admin_panel(update, context)

    async def handle_create_tour(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик создания тура"""
        if not self.is_admin(update.effective_user.id):
            await update.callback_query.answer("⛔️ У вас нет прав администратора.")
            return

        await update.callback_query.answer()
        await update.callback_query.message.reply_text(
            "📝 Создание нового тура\n\n"
            "Пожалуйста, отправьте данные тура в формате:\n\n"
            "Название\n"
            "Описание\n"
            "Цена\n"
            "Длительность (в днях)\n"
            "URL изображения\n"
            "Место\n"
            "Максимальное количество участников\n"
            "Доступные места\n"
            "Дата отправления (YYYY-MM-DD)\n"
            "Дата возвращения (YYYY-MM-DD)\n\n"
            "Например:\n"
            "Тур по Золотому кольцу\n"
            "Увлекательное путешествие по древним городам\n"
            "50000\n"
            "7\n"
            "https://example.com/image.jpg\n"
            "Москва\n"
            "20\n"
            "20\n"
            "2024-05-01\n"
            "2024-05-07"
        )
        context.user_data['creating_tour'] = True

    async def handle_tour_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик данных нового тура"""
        if not context.user_data.get('creating_tour'):
            return

        try:
            # Разбиваем текст на строки
            lines = update.message.text.split('\n')
            if len(lines) < 10:
                raise ValueError("Недостаточно данных")

            # Парсим данные
            title = lines[0].strip()
            description = lines[1].strip()
            price = float(lines[2].strip())
            duration = int(lines[3].strip())
            image_url = lines[4].strip()
            location = lines[5].strip()
            max_participants = int(lines[6].strip())
            available_spots = int(lines[7].strip())
            departure_date = datetime.strptime(lines[8].strip(), "%Y-%m-%d")
            return_date = datetime.strptime(lines[9].strip(), "%Y-%m-%d")

            # Создаем тур через API
            tour_data = {
                "title": title,
                "description": description,
                "price": price,
                "duration": duration,
                "image_url": image_url,
                "location": location,
                "max_participants": max_participants,
                "available_spots": available_spots,
                "departure_date": departure_date.isoformat(),
                "return_date": return_date.isoformat()
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.settings.API_URL}/api/v1/tours/",
                    json=tour_data,
                    headers={"Authorization": f"Bearer {self.settings.API_TOKEN}"}
                )

            if response.status_code == 200:
                await update.message.reply_text(
                    "✅ Тур успешно создан!\n\n"
                    f"Название: {title}\n"
                    f"Цена: {price} руб.\n"
                    f"Длительность: {duration} дней\n"
                    f"Место: {location}"
                )
            else:
                await update.message.reply_text(
                    "❌ Ошибка при создании тура. Пожалуйста, проверьте данные и попробуйте снова."
                )

        except Exception as e:
            await update.message.reply_text(
                "❌ Ошибка при создании тура. Пожалуйста, проверьте формат данных и попробуйте снова.\n"
                f"Ошибка: {str(e)}"
            )

        finally:
            context.user_data['creating_tour'] = False
            # Возвращаемся в админ-панель
            await self.handle_admin_panel(update, context)

    async def notify_admin_about_request(self, request_data: dict):
        """Отправляет уведомление администратору о новой заявке"""
        try:
            status_emoji = {
                "pending": "⏳",
                "approved": "✅",
                "rejected": "❌",
                "cancelled": "🚫"
            }.get(request_data.get('status', 'pending'), "❓")

            message = (
                f"🆕 Новая заявка!\n\n"
                f"ID: {request_data.get('id')}\n"
                f"Тур: {request_data.get('tour', {}).get('title', 'Не указан')}\n"
                f"Статус: {status_emoji} {request_data.get('status', 'pending')}\n"
                f"Дата создания: {request_data.get('created_at', 'Не указана')}\n\n"
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
            for admin_id in self.settings.ADMIN_IDS:
                try:
                    # Проверяем, существует ли чат
                    try:
                        chat = await self.application.bot.get_chat(admin_id)
                        if chat:
                            try:
                                await self.application.bot.send_message(
                                    chat_id=admin_id,
                                    text=message,
                                    reply_markup=reply_markup
                                )
                            except Exception as e:
                                logger.error(f"Error sending message to admin {admin_id}: {e}")
                                # Пробуем отправить сообщение без кнопок
                                try:
                                    await self.application.bot.send_message(
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
            logger.error(f"Error in notify_admin_about_request: {e}")

    async def handle_request_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик изменения статуса заявки"""
        query = update.callback_query
        await query.answer()

        if query.from_user.id not in settings.ADMIN_IDS:
            await query.message.reply_text("У вас нет прав для изменения статуса заявки.")
            return

        _, request_id, new_status = query.data.split("_")
        request_id = int(request_id)

        try:
            async with httpx.AsyncClient() as client:
                # Получаем текущие данные заявки
                response = await client.get(
                    f"{self.settings.API_URL}/api/v1/requests/{request_id}",
                    headers={"Authorization": f"Bearer {self.settings.API_TOKEN}"}
                )
                response.raise_for_status()
                request_data = response.json()

                # Обновляем статус заявки
                response = await client.patch(
                    f"{self.settings.API_URL}/api/v1/requests/{request_id}",
                    json={"status": new_status},
                    headers={"Authorization": f"Bearer {self.settings.API_TOKEN}"}
                )
                response.raise_for_status()

                # Отправляем уведомление об изменении статуса
                status_emoji = {
                    "pending": "⏳",
                    "approved": "✅",
                    "rejected": "❌",
                    "cancelled": "🚫"
                }.get(new_status, "❓")

                await query.message.reply_text(
                    f"Статус заявки #{request_id} изменен на {status_emoji} {new_status}"
                )

                # Показываем обновленный список заявок
                await self.list_requests(update, context)

                # Отправляем уведомление всем администраторам
                await self.notify_admin_about_request(request_data)

        except Exception as e:
            logger.error(f"Error updating request status: {e}")
            await query.message.reply_text(
                "❌ Произошла ошибка при обновлении статуса заявки"
            )

    async def delete_previous_category_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Удаляет предыдущие сообщения категории"""
        if "last_category_message_ids" in context.user_data:
            for message_id in context.user_data["last_category_message_ids"]:
                try:
                    await context.bot.delete_message(
                        chat_id=update.effective_chat.id,
                        message_id=message_id
                    )
                except Exception as e:
                    logger.error(f"Error deleting message {message_id}: {e}")
            context.user_data["last_category_message_ids"] = []

    async def handle_admin_tours(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик просмотра списка туров"""
        query = update.callback_query
        await query.answer()

        if not self.is_admin(query.from_user.id):
            await query.message.reply_text("⛔️ У вас нет прав администратора.")
            return

        # Удаляем предыдущие сообщения категории
        await self.delete_previous_category_messages(update, context)

        db = SessionLocal()
        try:
            tours = db.query(models.Tour).all()
            if not tours:
                await query.message.reply_text("Туры не найдены.")
                return

            message_ids = []
            for tour in tours:
                message = (
                    f"📋 Тур #{tour.id}\n"
                    f"Название: {tour.title}\n"
                    f"Цена: {format_price(tour.price)}\n"
                    f"Длительность: {tour.duration} дней\n"
                    f"Место: {tour.location}\n"
                    f"Свободных мест: {tour.available_spots}/{tour.max_participants}\n"
                    f"{'🔥 Горящий тур' if tour.is_hot else ''}\n\n"
                    f"Описание:\n{tour.description}\n"
                )

                keyboard = [
                    [InlineKeyboardButton("🔄 Обновить статус", callback_data=f"tour_status_{tour.id}")],
                    [InlineKeyboardButton("📋 Все туры", callback_data="admin_tours")],
                    [InlineKeyboardButton("👥 Заявки", callback_data="admin_requests")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                sent_message = await query.message.reply_text(message, reply_markup=reply_markup)
                message_ids.append(sent_message.message_id)

            # Сохраняем ID сообщений для последующего удаления
            context.user_data["last_category_message_ids"] = message_ids

        finally:
            db.close()

    async def handle_admin_requests(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик просмотра списка заявок"""
        query = update.callback_query
        await query.answer()
        
        if not self.is_admin(query.from_user.id):
            await query.message.reply_text("⛔️ У вас нет прав администратора.")
            return

        # Удаляем предыдущие сообщения категории
        await self.delete_previous_category_messages(update, context)

        db = SessionLocal()
        try:
            requests = db.query(models.TravelRequest).all()
            if not requests:
                await query.message.reply_text("Заявки не найдены.")
                return

            message_ids = []
            for request in requests:
                status_emoji = {
                    "pending": "⏳",
                    "approved": "✅",
                    "rejected": "❌",
                    "cancelled": "🚫"
                }.get(request.status, "❓")

                message = (
                    f"👥 Заявка #{request.id}\n"
                    f"Тур: {request.tour.title}\n"
                    f"Статус: {status_emoji} {request.status}\n"
                    f"Дата: {format_datetime(request.created_at)}\n"
                )

                if request.user_id:
                    message += f"Пользователь: {request.user.username}\n"
                else:
                    message += (
                        f"Гость: {request.guest_name}\n"
                        f"Email: {request.guest_email}\n"
                        f"Телефон: {request.guest_phone}\n"
                    )

                if request.comment:
                    message += f"Комментарий: {request.comment}\n"

                # Добавляем кнопки управления статусом
                keyboard = []
                for new_status in ["pending", "approved", "rejected", "cancelled"]:
                    if new_status != request.status:
                        keyboard.append([
                            InlineKeyboardButton(
                                f"Установить статус: {new_status}",
                                callback_data=f"status_{request.id}_{new_status}"
                            )
                        ])
                
                # Добавляем навигационные кнопки
                keyboard.extend([
                    [InlineKeyboardButton("📋 Все туры", callback_data="admin_tours")],
                    [InlineKeyboardButton("👥 Все заявки", callback_data="admin_requests")]
                ])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                sent_message = await query.message.reply_text(message, reply_markup=reply_markup)
                message_ids.append(sent_message.message_id)
            
            # Сохраняем ID сообщений для последующего удаления
            context.user_data["last_category_message_ids"] = message_ids

        finally:
            db.close()

    async def handle_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик возврата в главное меню"""
        query = update.callback_query
        await query.answer()

        if not self.is_admin(query.from_user.id):
            await query.message.reply_text("⛔️ У вас нет прав администратора.")
            return

        # Удаляем предыдущие сообщения категории
        await self.delete_previous_category_messages(update, context)

        keyboard = [
            [InlineKeyboardButton("📋 Список туров", callback_data="admin_tours")],
            [InlineKeyboardButton("👥 Заявки", callback_data="admin_requests")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        sent_message = await query.message.edit_text(
            "Добро пожаловать в бот администратора Вкусных Маршрутов!\n"
            "Используйте /help для просмотра доступных команд.",
            reply_markup=reply_markup
        )
        context.user_data["last_category_message_ids"] = [sent_message.message_id]

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик callback-запросов"""
        query = update.callback_query
        await query.answer()

        if query.from_user.id not in settings.ADMIN_IDS:
            await query.message.reply_text(
                "Этот бот предназначен только для администраторов. "
                "Пожалуйста, обратитесь к администратору для получения доступа."
            )
            return

        # Обработка различных callback_data
        if query.data == "admin_panel":
            await self.admin_panel(update, context)
        elif query.data == "list_tours":
            await self.list_tours(update, context)
        elif query.data == "list_requests":
            await self.list_requests(update, context)
        elif query.data == "create_tour":
            await self.create_tour(update, context)
        elif query.data == "help":
            await self.help(update, context)
        elif query.data == "admin_tours":
            await self.handle_admin_tours(update, context)
        elif query.data == "admin_requests":
            await self.handle_admin_requests(update, context)
        elif query.data == "main_menu":
            await self.handle_main_menu(update, context)
        elif query.data.startswith("status_"):
            await self.handle_request_status(update, context)
        else:
            await query.message.reply_text("❌ Неизвестная команда")

    def run(self):
        """Запуск бота"""
        self.application.run_polling() 