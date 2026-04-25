from app.db import SessionLocal
from app.models.entities import Message, MessageStatus
from app.services.messages import process_message
from app.services.queue import DLQ_QUEUE, MAIN_QUEUE, RETRY_QUEUE, queue_service
from app.services.state import runtime_controls


def _room(client):
    response = client.post("/api/rooms", json={"name": "infra"})
    assert response.status_code == 200
    return response.json()["id"]


def test_idempotency_reuses_existing_message(client):
    room_id = _room(client)
    payload = {"room_id": room_id, "username": "ada", "content": "hello", "client_message_id": "same-id"}

    first = client.post("/api/messages", json=payload)
    second = client.post("/api/messages", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]
    assert first.json()["sequence_number"] == second.json()["sequence_number"] == 1


def test_rate_limiting_returns_429(client):
    room_id = _room(client)

    for idx in range(10):
        response = client.post(
            "/api/messages",
            json={"room_id": room_id, "username": "rate-user", "content": f"m{idx}", "client_message_id": f"id-{idx}"},
        )
        assert response.status_code == 200

    blocked = client.post(
        "/api/messages",
        json={"room_id": room_id, "username": "rate-user", "content": "blocked", "client_message_id": "id-blocked"},
    )

    assert blocked.status_code == 429
    assert blocked.json()["detail"]["error"] == "rate_limited"


def test_message_persistence_and_delivery(client):
    room_id = _room(client)
    response = client.post(
        "/api/messages",
        json={"room_id": room_id, "username": "grace", "content": "persist me", "client_message_id": "persist-1"},
    )
    message_id = response.json()["id"]

    with SessionLocal() as db:
        message = db.get(Message, message_id)
        assert message is not None
        assert message.status == MessageStatus.queued

    assert queue_service.local_depth(MAIN_QUEUE) == 1


def test_retry_logic_moves_to_dead_letter(client):
    room_id = _room(client)
    response = client.post(
        "/api/messages",
        json={"room_id": room_id, "username": "linus", "content": "fail me", "client_message_id": "fail-1"},
    )
    message_id = response.json()["id"]
    runtime_controls.failure_rate = 100

    with SessionLocal() as db:
        for _ in range(3):
            db.expire_all()
            db_message = db.get(Message, message_id)
            db_message.status = MessageStatus.queued
            db.commit()
            import asyncio

            asyncio.run(process_message(db, message_id))

        db.expire_all()
        message = db.get(Message, message_id)
        assert message.status == MessageStatus.dead_lettered
        assert message.retry_count == 3

    assert queue_service.local_depth(DLQ_QUEUE) == 1
    assert queue_service.local_depth(RETRY_QUEUE) >= 2
