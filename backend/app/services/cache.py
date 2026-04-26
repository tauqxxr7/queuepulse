import time
from collections import defaultdict, deque

try:
    import redis
except ModuleNotFoundError:  # Local demo mode can run without the Redis client installed.
    redis = None

from app.config import get_settings


class CacheService:
    def __init__(self) -> None:
        self._redis = None
        self._presence: set[str] = set()
        self._room_presence: dict[str, set[str]] = defaultdict(set)
        self._limits: dict[str, deque[float]] = defaultdict(deque)
        settings = get_settings()
        if redis and settings.use_external_services and settings.redis_url:
            try:
                self._redis = redis.Redis.from_url(settings.redis_url, decode_responses=True, socket_connect_timeout=1)
                self._redis.ping()
            except Exception:
                self._redis = None

    def mark_online(self, username: str, room_id: str | None = None) -> None:
        if self._redis:
            self._redis.sadd("presence:users", username)
            if room_id:
                self._redis.sadd(f"presence:room:{room_id}", username)
        self._presence.add(username)
        if room_id:
            self._room_presence[room_id].add(username)

    def mark_offline(self, username: str, room_id: str | None = None) -> None:
        if self._redis:
            self._redis.srem("presence:users", username)
            if room_id:
                self._redis.srem(f"presence:room:{room_id}", username)
        self._presence.discard(username)
        if room_id:
            self._room_presence[room_id].discard(username)

    def active_users(self) -> int:
        if self._redis:
            return int(self._redis.scard("presence:users"))
        return len(self._presence)

    def active_rooms(self) -> int:
        if self._redis:
            keys = self._redis.keys("presence:room:*")
            return sum(1 for key in keys if self._redis.scard(key) > 0)
        return sum(1 for users in self._room_presence.values() if users)

    def allow_message(self, username: str) -> tuple[bool, int]:
        settings = get_settings()
        now = time.time()
        if self._redis:
            key = f"rate:{username}:{int(now // settings.rate_limit_window_seconds)}"
            count = self._redis.incr(key)
            self._redis.expire(key, settings.rate_limit_window_seconds + 1)
            return count <= settings.rate_limit_messages, max(0, settings.rate_limit_messages - int(count))

        bucket = self._limits[username]
        while bucket and now - bucket[0] > settings.rate_limit_window_seconds:
            bucket.popleft()
        if len(bucket) >= settings.rate_limit_messages:
            return False, 0
        bucket.append(now)
        return True, settings.rate_limit_messages - len(bucket)


cache_service = CacheService()
