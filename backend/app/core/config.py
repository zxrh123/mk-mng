 """Application-wide configuration management using Pydantic settings."""

 from __future__ import annotations

 from functools import lru_cache
 from pathlib import Path
 from typing import Literal

 from pydantic import AnyHttpUrl, Field, SecretStr
 from pydantic_settings import BaseSettings, SettingsConfigDict


 class Settings(BaseSettings):
     """Runtime configuration values for the backend service."""

     model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")

     app_name: str = "MikroTik AI Control Plane"
     environment: Literal["development", "staging", "production"] = "development"
     api_prefix: str = "/api"
     websocket_path: str = "/ws/ai"

     database_url: str = Field(
         default="postgresql+asyncpg://postgres:postgres@localhost:5432/mikrotik_ai",
         validation_alias="DB_URL",
     )
     redis_url: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")

     openai_api_key: SecretStr | None = Field(default=None, validation_alias="OPENAI_API_KEY")
     openai_model: str = Field(default="gpt-4o", validation_alias="OPENAI_MODEL")
     gemini_api_key: SecretStr | None = Field(default=None, validation_alias="GEMINI_API_KEY")
     gemini_model: str = Field(default="gemini-1.5-pro", validation_alias="GEMINI_MODEL")

     routeros_host: str = Field(default="192.168.88.1", validation_alias="ROUTEROS_HOST")
     routeros_username: str = Field(default="admin", validation_alias="ROUTEROS_USER")
     routeros_password: SecretStr | None = Field(default=None, validation_alias="ROUTEROS_PASSWORD")
     routeros_use_tls: bool = Field(default=False, validation_alias="ROUTEROS_TLS")

     ai_decision_threshold: float = Field(default=0.6, ge=0, le=1)
     ai_feedback_learning_rate: float = Field(default=0.1, ge=0, le=1)

     allow_auto_execute: bool = Field(default=False, validation_alias="AUTO_EXECUTE")
     snapshot_before_execute: bool = Field(default=True)

     client_origin: AnyHttpUrl | None = Field(default=None, validation_alias="CLIENT_ORIGIN")

     knowledge_base_dir: Path = Field(
         default=Path("./storage/knowledge_base"), validation_alias="KB_DIR"
     )

     class Security(BaseSettings):  # type: ignore[misc]
         model_config = SettingsConfigDict(env_prefix="SECURITY_")

         jwt_secret_key: SecretStr = Field(default=SecretStr("change-me"))
         jwt_algorithm: str = Field(default="HS256")
         access_token_expire_minutes: int = Field(default=60)

     security: Security = Security()


 @lru_cache
 def get_settings() -> Settings:
     """Return application settings with caching."""

     settings = Settings()
     settings.knowledge_base_dir.mkdir(parents=True, exist_ok=True)
     return settings


 settings = get_settings()

