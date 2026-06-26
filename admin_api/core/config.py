from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    SECRET_KEY: str
    ADMIN_EMAIL: str
    ADMIN_PASSWORD_HASH: str
    
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    POSTGRES_URL: str
    REDIS_URL: str
    FRONTEND_URL: str = "http://localhost:5001"
    SCRAPER_LOG_PATH: str = "../scraper/logs/scraper.log"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
