import os
from pydantic_settings import BaseSettings
from datetime import timedelta

class Settings(BaseSettings):
    # Base settings
    API_V1_STR: str = "/api/v1"  # This means all API endpoints will start with /api/v1/
    PROJECT_NAME: str = "Smart Task Management"
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./api_gateway.db"
    
    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-jwt")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Service URLs
    TASK_SERVICE_URL: str = "http://localhost:8001/api/v1"

    # Redis settings
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # API settings
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()


