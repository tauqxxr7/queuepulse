from dataclasses import dataclass

try:
    import redis
except ModuleNotFoundError:  # Local demo mode can run without the Redis client installed.
    redis = None

from app.config import get_settings


@dataclass
class RuntimeControls:
    failure_rate: float = get_settings().failure_rate
    worker_delay_ms: int = get_settings().worker_delay_ms
    consumer_paused: bool = False


runtime_controls = RuntimeControls()

_redis_client = None


def _redis():
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    settings = get_settings()
    if redis is None or settings.is_local or not settings.redis_url:
        return None
    try:
        _redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True, socket_connect_timeout=1)
        _redis_client.ping()
        return _redis_client
    except Exception:
        _redis_client = None
        return None


def _get_float(key: str, fallback: float) -> float:
    client = _redis()
    if not client:
        return fallback
    value = client.get(key)
    return float(value) if value is not None else fallback


def _get_int(key: str, fallback: int) -> int:
    client = _redis()
    if not client:
        return fallback
    value = client.get(key)
    return int(value) if value is not None else fallback


def _get_bool(key: str, fallback: bool) -> bool:
    client = _redis()
    if not client:
        return fallback
    value = client.get(key)
    return value == "1" if value is not None else fallback


def set_failure_rate(value: float) -> float:
    runtime_controls.failure_rate = value
    client = _redis()
    if client:
        client.set("runtime:failure_rate", value)
    return value


def get_failure_rate() -> float:
    return _get_float("runtime:failure_rate", runtime_controls.failure_rate)


def set_worker_delay_ms(value: int) -> int:
    runtime_controls.worker_delay_ms = value
    client = _redis()
    if client:
        client.set("runtime:worker_delay_ms", value)
    return value


def get_worker_delay_ms() -> int:
    return _get_int("runtime:worker_delay_ms", runtime_controls.worker_delay_ms)


def set_consumer_paused(value: bool) -> bool:
    runtime_controls.consumer_paused = value
    client = _redis()
    if client:
        client.set("runtime:consumer_paused", "1" if value else "0")
    return value


def is_consumer_paused() -> bool:
    return _get_bool("runtime:consumer_paused", runtime_controls.consumer_paused)
