from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_SERVERS: List[str] = ["220.88.3.118:6433", "192.168.0.5", "192.168.1.5"]
    DB_NAME: str = "PFMES"
    DB_UID: str = "SA"
    DB_PWD: str = "itscore1!"
    LOG_PATH: str = "logs/backend.log"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
