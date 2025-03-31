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
        return user_id in self.settings.ADMIN_IDS

    def setup_handlers(self):
        # Обработчики команд
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("admin", self.admin_panel))
        
        # Обработчики callback-запросов
        self.application.add_handler(CallbackQueryHandler(self.handle_admin_tours, pattern="^admin_tours$"))
        self.application.add_handler(CallbackQueryHandler(self.handle_create_tour, pattern="^create_tour$"))
        self.application.add_handler(CallbackQueryHandler(self.handle_admin_requests, pattern="^admin_requests$"))
        self.application.add_handler(CallbackQueryHandler(self.handle_request_status, pattern="^status_\d+_\w+$"))
        self.application.add_handler(CallbackQueryHandler(self.handle_main_menu, pattern="^main_menu$"))
        
        # Обработчики сообщений
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
        """Обработчик команды /admin и callback-запросов для админ-панели"""
        query = update.callback_query
        user_id = query.from_user.id if query else update.effective_user.id

        if not self.is_admin(user_id):
            if query:
                await query.answer("⛔️ У вас нет прав администратора.")
            else:
                await update.message.reply_text("⛔️ У вас нет прав администратора.")
            return

        keyboard = [
            [InlineKeyboardButton("📋 Список туров", callback_data="admin_tours")],
            [InlineKeyboardButton("📝 Создать тур", callback_data="create_tour")],
            [InlineKeyboardButton("📨 Заявки", callback_data="admin_requests")],
            [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message_text = (
            "🔧 Панель администратора\n\n"
            "Выберите действие:"
        )

        if query:
            await query.answer()
            await query.message.edit_text(message_text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(message_text, reply_markup=reply_markup)

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

    async def handle_request_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик изменения статуса заявки"""
        query = update.callback_query
        await query.answer()

        if query.from_user.id not in settings.ADMIN_IDS:
            await query.message.reply_text("У вас нет прав для изменения статуса заявки.")
            return

        _, request_id, new_status = query.data.split("_")
        request_id = int(request_id)

        db = SessionLocal()
        try:
            request = db.query(models.TravelRequest).filter(models.TravelRequest.id == request_id).first()
            if not request:
                await query.message.reply_text("Заявка не найдена.")
                return

            old_status = request.status
            request.status = new_status

            if new_status == "approved" and old_status != "approved":
                if request.tour.available_spots > 0:
                    request.tour.available_spots -= 1
                else:
                    await query.message.reply_text("Нет доступных мест для этого тура.")
                    return

            db.commit()

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
            await self.show_requests_list(query)

        finally:
            db.close()

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        if update.effective_user.id not in settings.ADMIN_IDS:
            await update.message.reply_text(
                "Этот бот предназначен только для администраторов. "
                "Пожалуйста, обратитесь к администратору для получения доступа."
            )
            return

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
                    await update.message.reply_text(
                        "✅ Тур успешно создан!\n\n"
                        f"Название: {title}\n"
                        f"Цена: {price} руб.\n"
                        f"Длительность: {duration} дней\n"
                        f"Место: {location}"
                    )
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

    async def handle_admin_tours(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик просмотра списка туров"""
        query = update.callback_query
        await query.answer()

        if not self.is_admin(query.from_user.id):
            await query.message.reply_text("⛔️ У вас нет прав администратора.")
            return

        db = SessionLocal()
        try:
            tours = db.query(models.Tour).all()
            if not tours:
                await query.message.reply_text("Туры не найдены.")
                return

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
                await query.message.reply_text(message, reply_markup=reply_markup)

        finally:
            db.close()

    async def handle_admin_requests(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик просмотра списка заявок"""
        query = update.callback_query
        await query.answer()

        if not self.is_admin(query.from_user.id):
            await query.message.reply_text("⛔️ У вас нет прав администратора.")
            return

        db = SessionLocal()
        try:
            requests = db.query(models.TravelRequest).all()
            if not requests:
                await query.message.reply_text("Заявки не найдены.")
                return

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
                await query.message.reply_text(message, reply_markup=reply_markup)

        finally:
            db.close()

    async def handle_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик возврата в главное меню"""
        query = update.callback_query
        await query.answer()

        if not self.is_admin(query.from_user.id):
            await query.message.reply_text("⛔️ У вас нет прав администратора.")
            return

        keyboard = [
            [InlineKeyboardButton("📋 Список туров", callback_data="admin_tours")],
            [InlineKeyboardButton("👥 Заявки", callback_data="admin_requests")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(
            "Добро пожаловать в бот администратора Вкусных Маршрутов!\n"
            "Используйте /help для просмотра доступных команд.",
            reply_markup=reply_markup
        )

    def run(self):
        """Запуск бота"""
        self.application.run_polling() 