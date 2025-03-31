from pydantic_settings import BaseSettings
from typing import List, Optional
from pydantic import field_validator

class Settings(BaseSettings):
    # Настройки базы данных
    DATABASE_URL: str = "sqlite:///./vkusny_marshruty.db"
    DB_PASSWORD: str
    
    # Настройки Telegram бота
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_GROUP_ID: str
    ADMIN_IDS: str  # Changed to str, will be converted to List[int] in validator
    
    # Настройки безопасности
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Настройки API
    API_URL: str = "http://localhost:8000"
    API_TOKEN: str = "your-api-token-here"
    
    # Настройки приложения
    APP_NAME: str = "Вкусные Маршруты"
    DEBUG: bool = True
    
    # Admin
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str

    @field_validator('ADMIN_IDS')
    def parse_admin_ids(cls, v):
        """Преобразует строку с ID администраторов в список целых чисел"""
        if not v:
            return []
        return [int(x.strip()) for x in v.split(',')]

    @field_validator('ACCESS_TOKEN_EXPIRE_MINUTES')
    def parse_token_expire(cls, v: str) -> int:
        try:
            return int(v)
        except ValueError:
            raise ValueError(f'Invalid ACCESS_TOKEN_EXPIRE_MINUTES format. Expected integer, got {v}')

    @field_validator('DEBUG')
    def parse_debug(cls, v: str) -> bool:
        return str(v).lower() == 'true'

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings() 