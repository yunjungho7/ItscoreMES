import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_ENV: str = "development"
    
    DB_SERVERS: List[str] = ["220.88.3.118:6433", "192.168.0.5", "192.168.1.5"]
    DB_NAME: str = "PFMES"
    DB_UID: str = "SA"
    DB_PWD: str = "itscore1!"
    LOG_PATH: str = "logs/backend.log"
    
    # 기본적으로 .env를 읽고, 환경 변수로 지정된 경우 해당 파일을 읽음
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        extra="ignore"
    )

settings = Settings()
