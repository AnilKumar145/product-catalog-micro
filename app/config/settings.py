"""Application configuration settings."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    APP_NAME: str = "Catalog Service"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Enterprise catalog service for BT simulation"
    
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    AUTH_SERVICE_URL: str
    
    EXTERNAL_API_TIMEOUT: int = 5
    EXTERNAL_API_MAX_RETRIES: int = 3
    
    REDIS_URL: str
    
    RABBITMQ_URL: str
    
    RATE_LIMIT_PER_MINUTE: int = 60
    
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    
    LOG_LEVEL: str = "INFO"
    AUDIT_LOG_FILE: str = "logs/audit.log"
    ERROR_LOG_FILE: str = "logs/error.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
