from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Vkusny Marshruty"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str
    
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_GROUP_ID: str
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings() 