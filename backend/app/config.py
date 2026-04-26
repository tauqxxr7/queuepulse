import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


def _load_dotenv() -> None:
    env_path = Path(".env")
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


def _optional(name: str) -> str | None:
    value = os.getenv(name)
    return value if value else None


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    app_name: str = "QueuePulse"
    env: str = "local"
    database_url: str = "sqlite:///./queuepulse.db"
    redis_url: str | None = None
    rabbitmq_url: str | None = None
    frontend_origin: str = "http://localhost:3000"
    rate_limit_messages: int = 10
    rate_limit_window_seconds: int = 10
    max_retries: int = 3
    failure_rate: float = 0
    worker_delay_ms: int = 100
    gemini_api_key: str | None = None

    @property
    def is_local(self) -> bool:
        return self.env.lower() == "local"

    @property
    def use_external_services(self) -> bool:
        return self.env.lower() == "docker"


@lru_cache
def get_settings() -> Settings:
    _load_dotenv()
    failure_rate = max(0.0, min(100.0, _float("FAILURE_RATE", 0)))
    worker_delay_ms = max(0, _int("WORKER_DELAY_MS", 100))
    return Settings(
        app_name=_env("APP_NAME", "QueuePulse"),
        env=os.getenv("ENV") or os.getenv("ENVIRONMENT") or "local",
        database_url=_env("DATABASE_URL", "sqlite:///./queuepulse.db"),
        redis_url=_optional("REDIS_URL"),
        rabbitmq_url=_optional("RABBITMQ_URL"),
        frontend_origin=_env("FRONTEND_ORIGIN", "http://localhost:3000"),
        rate_limit_messages=max(1, _int("RATE_LIMIT_MESSAGES", 10)),
        rate_limit_window_seconds=max(1, _int("RATE_LIMIT_WINDOW_SECONDS", 10)),
        max_retries=max(1, _int("MAX_RETRIES", 3)),
        failure_rate=failure_rate,
        worker_delay_ms=worker_delay_ms,
        gemini_api_key=_optional("GEMINI_API_KEY"),
    )
