from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "QueuePulse"
    environment: str = "development"
    database_url: str = "sqlite:///./queuepulse.db"
    redis_url: str | None = None
    rabbitmq_url: str | None = None
    frontend_origin: str = "http://localhost:3000"
    rate_limit_messages: int = 10
    rate_limit_window_seconds: int = 10
    max_retries: int = 3
    failure_rate: float = Field(default=0, ge=0, le=100)
    worker_delay_ms: int = Field(default=100, ge=0)
    gemini_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
