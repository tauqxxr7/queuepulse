import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///./test_queuepulse.db"
os.environ["REDIS_URL"] = ""
os.environ["RABBITMQ_URL"] = ""
os.environ["RATE_LIMIT_MESSAGES"] = "10"
os.environ["RATE_LIMIT_WINDOW_SECONDS"] = "10"
os.environ["WORKER_DELAY_MS"] = "0"

from app.config import get_settings  # noqa: E402

get_settings.cache_clear()

from app.db import Base, engine, init_db  # noqa: E402
from app.main import app  # noqa: E402
from app.services.cache import cache_service  # noqa: E402
from app.services.queue import DLQ_QUEUE, MAIN_QUEUE, RETRY_QUEUE, queue_service  # noqa: E402
from app.services.state import runtime_controls  # noqa: E402


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine)
    init_db()
    cache_service._presence.clear()
    cache_service._room_presence.clear()
    cache_service._limits.clear()
    queue_service._local[MAIN_QUEUE].clear()
    queue_service._local[RETRY_QUEUE].clear()
    queue_service._local[DLQ_QUEUE].clear()
    runtime_controls.failure_rate = 0
    runtime_controls.worker_delay_ms = 0
    runtime_controls.consumer_paused = False
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    Path("test_queuepulse.db").unlink(missing_ok=True)


@pytest.fixture()
def client():
    return TestClient(app)
