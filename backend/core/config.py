from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_SERVERS: List[str] = ["220.88.3.118:6433", "192.168.0.5", "192.168.1.5"]
    DB_NAME: str = "PFMES"
    DB_UID: str = "SA"
    DB_PWD: str = "itscore1!"
    LOG_PATH: str = "logs/backend.log"
    
    # JWT
    JWT_SECRET_KEY: str = "yoursecretkeyhere"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    
    # SMTP
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "your_email@gmail.com"
    SMTP_PASSWORD: str = "your_app_password"
    SMTP_FROM_EMAIL: str = "your_email@gmail.com"
    
    # Internal Network
    INTERNAL_IP_RANGES: str = "127.0.0.1,192.168.0.0/16"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
