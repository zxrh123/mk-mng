"""
Application Configuration
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/mikrotik_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # Google Gemini
    GEMINI_API_KEY: str = ""
    
    # Security
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # MikroTik Default
    MIKROTIK_DEFAULT_HOST: str = "192.168.88.1"
    MIKROTIK_DEFAULT_USER: str = "admin"
    MIKROTIK_DEFAULT_PASSWORD: str = ""
    
    # AI Settings
    AI_AUTO_EXECUTE: bool = False
    AI_DRY_RUN: bool = True
    AI_ENABLE_LEARNING: bool = True
    
    # Monitoring
    MONITORING_INTERVAL: int = 5
    ALERT_THRESHOLD_CPU: int = 80
    ALERT_THRESHOLD_RAM: int = 85
    ALERT_THRESHOLD_LATENCY: int = 100
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
