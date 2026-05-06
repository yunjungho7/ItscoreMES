import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_ENV: str = "development"
    
    # DB 설정 (기본값은 로컬/개발용, .env에서 오버라이드 가능)
    DB_SERVERS: List[str] = ["127.0.0.1"]
    DB_NAME: str = "PFMES"
    DB_UID: str = "SA"
    DB_PWD: str = "itscore1!"
    LOG_PATH: str = "logs/backend.log"
    
    # JWT 보안 설정
    JWT_SECRET_KEY: str = "itscore-mes-secret-key-2024"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    
    # 메일 및 기타 설정
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # 환경 변수 ENV_FILE에 지정된 파일을 로드
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        extra="ignore"
    )

settings = Settings()
