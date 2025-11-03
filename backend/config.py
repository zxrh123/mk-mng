from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """
    ??????? ?????? ????????
    System Configuration Settings
    """
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://mikrotik_user:password@localhost:5432/mikrotik_ai")
    DATABASE_SYNC_URL: str = os.getenv("DATABASE_SYNC_URL", "postgresql://mikrotik_user:password@localhost:5432/mikrotik_ai")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # AI Models
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    GOOGLE_GEMINI_API_KEY: str = os.getenv("GOOGLE_GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-pro")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # MikroTik
    MIKROTIK_DEFAULT_PORT: int = 8728
    MIKROTIK_SSH_PORT: int = 22
    MIKROTIK_API_SSL: bool = True
    
    # System Configuration
    AUTO_EXECUTE: bool = os.getenv("AUTO_EXECUTE", "false").lower() == "true"
    ENABLE_AUTO_HEAL: bool = True
    ENABLE_LEARNING: bool = True
    MAX_CONCURRENT_TASKS: int = 10
    LOG_LEVEL: str = "INFO"
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Monitoring
    MONITORING_INTERVAL: int = 30
    ALERT_THRESHOLD_CPU: int = 85
    ALERT_THRESHOLD_RAM: int = 90
    ALERT_THRESHOLD_LATENCY: int = 200
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
