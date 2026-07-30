"""Environment-driven settings shared across Python services."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Safe local defaults matching `.env.example`."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"

    database_url: str = (
        "postgresql+psycopg://agent_reliability:agent_reliability@localhost:5432/agent_reliability"
    )
    redis_url: str = "redis://localhost:6379/0"
    rabbitmq_url: str = "amqp://agent_reliability:agent_reliability@localhost:5672/"

    orchestrator_url: str = "http://localhost:8001"
    artifact_storage_path: str = ".data/artifacts"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    orchestrator_host: str = "0.0.0.0"
    orchestrator_port: int = 8001


@lru_cache
def get_settings() -> Settings:
    """Return a process-wide settings instance."""
    return Settings()
