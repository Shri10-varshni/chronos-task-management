import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Base settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Task Service"
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./task_service.db"
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379/1"
    REDIS_TTL_TASKS: int = 3600  # 1 hour
    REDIS_TTL_TASK_LIST: int = 300  # 5 minutes
    
    # API settings
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        case_sensitive = True

settings = Settings()
