from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from app.core.config import settings
from app.db.database import SessionLocal
from app.db import models
from app.schemas import schemas
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TravelBot:
    def __init__(self):
        self.application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        self.setup_handlers()

    def setup_handlers(self):
        # Команды
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("tours", self.list_tours))
        self.application.add_handler(CommandHandler("hot", self.hot_tours))
        
        # Обработчики callback-запросов
        self.application.add_handler(CallbackQueryHandler(self.tour_details, pattern="^tour_"))
        self.application.add_handler(CallbackQueryHandler(self.create_request, pattern="^request_"))

    async def initialize(self):
        await self.application.initialize()

    async def start(self):
        await self.application.start()
        await self.application.run_polling()

    async def stop(self):
        await self.application.stop()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        welcome_message = (
            "👋 Добро пожаловать в бот Vkusny Marshruty!\n\n"
            "Здесь вы можете найти горящие путевки по отличным ценам.\n"
            "Используйте /help для просмотра доступных команд."
        )
        await update.message.reply_text(welcome_message)

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_message = (
            "📋 Доступные команды:\n\n"
            "/tours - Показать все доступные туры\n"
            "/hot - Показать горящие предложения\n"
            "/help - Показать это сообщение"
        )
        await update.message.reply_text(help_message)

    async def list_tours(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать список всех туров"""
        db = SessionLocal()
        try:
            tours = db.query(models.Tour).all()
            if not tours:
                await update.message.reply_text("К сожалению, сейчас нет доступных туров.")
                return

            message = "🌍 Доступные туры:\n\n"
            for tour in tours:
                message += f"📍 {tour.title}\n"
                message += f"🏖 {tour.country}, {tour.city}\n"
                message += f"💰 Цена: {tour.price}₽ (было {tour.original_price}₽)\n"
                message += f"📅 {tour.departure_date.strftime('%d.%m.%Y')} - {tour.return_date.strftime('%d.%m.%Y')}\n"
                message += f"🎫 Осталось мест: {tour.available_spots}\n\n"

            await update.message.reply_text(message)
        finally:
            db.close()

    async def hot_tours(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать горящие предложения"""
        db = SessionLocal()
        try:
            tours = db.query(models.Tour).filter(models.Tour.is_hot == True).all()
            if not tours:
                await update.message.reply_text("К сожалению, сейчас нет горящих предложений.")
                return

            message = "🔥 Горящие предложения:\n\n"
            for tour in tours:
                keyboard = [[InlineKeyboardButton("Подробнее", callback_data=f"tour_{tour.id}")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                message = (
                    f"📍 {tour.title}\n"
                    f"🏖 {tour.country}, {tour.city}\n"
                    f"💰 Цена: {tour.price}₽ (было {tour.original_price}₽)\n"
                    f"📅 {tour.departure_date.strftime('%d.%m.%Y')} - {tour.return_date.strftime('%d.%m.%Y')}\n"
                    f"🎫 Осталось мест: {tour.available_spots}\n"
                )
                await update.message.reply_text(message, reply_markup=reply_markup)
        finally:
            db.close()

    async def tour_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать детали тура"""
        query = update.callback_query
        await query.answer()
        
        tour_id = int(query.data.split('_')[1])
        db = SessionLocal()
        try:
            tour = db.query(models.Tour).filter(models.Tour.id == tour_id).first()
            if not tour:
                await query.message.reply_text("Тур не найден.")
                return

            message = (
                f"📋 Подробная информация о туре:\n\n"
                f"📍 {tour.title}\n"
                f"🏖 {tour.country}, {tour.city}\n"
                f"💰 Цена: {tour.price}₽ (было {tour.original_price}₽)\n"
                f"📅 {tour.departure_date.strftime('%d.%m.%Y')} - {tour.return_date.strftime('%d.%m.%Y')}\n"
                f"🎫 Осталось мест: {tour.available_spots}\n\n"
                f"📝 Описание:\n{tour.description}"
            )

            keyboard = [[InlineKeyboardButton("Оставить заявку", callback_data=f"request_{tour.id}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.reply_text(message, reply_markup=reply_markup)
        finally:
            db.close()

    async def create_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Создать заявку на тур"""
        query = update.callback_query
        await query.answer()
        
        tour_id = int(query.data.split('_')[1])
        db = SessionLocal()
        try:
            # Здесь должна быть логика создания заявки
            # В реальном приложении нужно будет добавить регистрацию пользователя
            await query.message.reply_text(
                "Для оформления заявки, пожалуйста, посетите наш сайт или свяжитесь с менеджером."
            )
        finally:
            db.close()

# Создаем экземпляр бота
bot = TravelBot() 