from functools import lru_cache
from typing import Any, List, Optional

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    # General
    project_name: str = "MikroTik AI Network Manager"
    environment: str = Field(default="development")
    log_level: str = Field(default="INFO")
    api_v1_str: str = Field(default="/api/v1")
    backend_cors_origins: List[str] = Field(default_factory=lambda: ["*"])

    # Database
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    postgres_user: str = Field(default="mikrotik_ai")
    postgres_password: SecretStr = Field(default=SecretStr("changeme"))
    postgres_db: str = Field(default="mikrotik_ai")
    postgres_sslmode: str = Field(default="prefer")

    # Cache / Broker
    redis_url: str = Field(default="redis://localhost:6379/0")

    # AI Providers
    openai_api_key: Optional[SecretStr] = Field(default=None)
    openai_model: str = Field(default="gpt-5.0-advanced")
    gemini_api_key: Optional[SecretStr] = Field(default=None)
    gemini_model: str = Field(default="gemini-1.5-pro-latest")

    # RouterOS
    routeros_hosts: List[str] = Field(default_factory=list)
    routeros_username: Optional[str] = None
    routeros_password: Optional[SecretStr] = None
    routeros_port: int = Field(default=8728)
    routeros_use_ssh: bool = Field(default=True)
    routeros_ssh_port: int = Field(default=22)

    # Automation guards
    auto_execute: bool = Field(default=False)
    snapshot_before_execute: bool = Field(default=True)
    dry_run_default: bool = Field(default=True)

    # Monitoring
    telemetry_interval_seconds: int = Field(default=30)
    anomaly_threshold_cpu: float = Field(default=0.85)
    anomaly_threshold_memory: float = Field(default=0.9)
    anomaly_threshold_interface_errors: int = Field(default=50)

    # Knowledge base
    knowledge_sources: List[str] = Field(
        default_factory=lambda: [
            "https://forum.mikrotik.com/viewforum.php?f=2",
            "https://wiki.mikrotik.com/wiki/Main_Page",
        ]
    )
    knowledge_refresh_minutes: int = Field(default=240)

    # Notifications / WebSocket
    notifications_channel: str = Field(default="ai-notifications")

    # Security
    jwt_secret_key: SecretStr = Field(default=SecretStr("supersecretkey"))
    jwt_algorithm: str = Field(default="HS256")

    # Observability
    enable_prometheus: bool = Field(default=True)

    # Feature flags
    enable_auto_heal: bool = Field(default=True)
    enable_knowledge_crawler: bool = Field(default=True)

    @property
    def database_url(self) -> str:
        password = self.postgres_password.get_secret_value()
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}?sslmode={self.postgres_sslmode}"
        )

    @field_validator("backend_cors_origins", "routeros_hosts", "knowledge_sources", mode="before")
    @classmethod
    def split_str(cls, value: Any) -> List[str]:  # type: ignore[override]
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
