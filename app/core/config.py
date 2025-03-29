from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    # Database
    db_host: str = "localhost"
    db_port: str = "5432"
    db_name: str = "vkusny_marshruty"
    db_user: str = os.getenv("DB_USER", "max")
    db_password: str = os.getenv("DB_PASSWORD", "")

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    # Telegram
    telegram_bot_token: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_group_id: Optional[str] = os.getenv("TELEGRAM_GROUP_ID")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "development_secret_key_123")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Admin
    admin_username: str = os.getenv("ADMIN_USERNAME", "admin")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "admin123")

    # Application
    app_name: str = os.getenv("APP_NAME", "Vkusny Marshruty")
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"

    # API Settings
    PROJECT_NAME: str = "Vkusny Marshruty API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

settings = Settings()
