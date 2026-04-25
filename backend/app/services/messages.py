import asyncio
import random
import time
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.entities import (
    DeliveryAttempt,
    Message,
    MessageStatus,
    MessageStatusEvent,
    Room,
    RoomMember,
    RoomSequence,
    User,
)
from app.schemas import MessageCreate
from app.services.cache import cache_service
from app.services.queue import queue_service
from app.services.state import get_failure_rate, get_worker_delay_ms, is_consumer_paused
from app.websocket.manager import websocket_manager


def get_or_create_user(db: Session, username: str) -> User:
    user = db.scalar(select(User).where(User.username == username))
    if user:
        return user
    user = User(username=username)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_room(db: Session, name: str) -> Room:
    room = db.scalar(select(Room).where(Room.name == name))
    if room:
        return room
    room = Room(name=name)
    db.add(room)
    db.flush()
    db.add(RoomSequence(room_id=room.id, next_sequence=1))
    db.commit()
    db.refresh(room)
    return room


def _next_sequence(db: Session, room_id: str) -> int:
    seq = db.get(RoomSequence, room_id)
    if not seq:
        seq = RoomSequence(room_id=room_id, next_sequence=1)
        db.add(seq)
        db.flush()
    current = seq.next_sequence
    seq.next_sequence += 1
    return current


def _record_status(db: Session, message: Message, status: MessageStatus, event_type: str, detail: str | None = None) -> None:
    message.status = status
    message.updated_at = datetime.now(timezone.utc)
    if detail:
        message.failure_reason = detail
    db.add(MessageStatusEvent(message_id=message.id, event_type=event_type, status=status, detail=detail))


def serialize_message(message: Message) -> dict:
    return {
        "id": message.id,
        "room_id": message.room_id,
        "user_id": message.user_id,
        "username": message.user.username if message.user else "",
        "client_message_id": message.client_message_id,
        "content": message.content,
        "sequence_number": message.sequence_number,
        "status": message.status.value,
        "retry_count": message.retry_count,
        "failure_reason": message.failure_reason,
        "delivery_latency_ms": message.delivery_latency_ms,
        "created_at": message.created_at,
    }


async def submit_message(db: Session, payload: MessageCreate) -> Message:
    allowed, remaining = cache_service.allow_message(payload.username)
    if not allowed:
        raise HTTPException(status_code=429, detail={"error": "rate_limited", "message": "Message rate limit exceeded", "remaining": remaining})

    room = db.get(Room, payload.room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    existing = db.scalar(
        select(Message).where(Message.room_id == payload.room_id, Message.client_message_id == payload.client_message_id)
    )
    if existing:
        return existing

    user = get_or_create_user(db, payload.username)
    if not db.scalar(select(RoomMember).where(RoomMember.room_id == room.id, RoomMember.user_id == user.id)):
        db.add(RoomMember(room_id=room.id, user_id=user.id))

    message = Message(
        room_id=room.id,
        user_id=user.id,
        client_message_id=payload.client_message_id,
        content=payload.content,
        sequence_number=_next_sequence(db, room.id),
        status=MessageStatus.queued,
    )
    db.add(message)
    db.flush()
    db.add(MessageStatusEvent(message_id=message.id, event_type="message.created", status=MessageStatus.queued))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return db.scalar(select(Message).where(Message.room_id == payload.room_id, Message.client_message_id == payload.client_message_id))
    db.refresh(message)
    await queue_service.publish_message(message.id)
    await websocket_manager.broadcast(room.id, {"type": "message.status", "message_id": message.id, "status": "queued"})
    return message


async def process_message(db: Session, message_id: str) -> None:
    if is_consumer_paused():
        await queue_service.publish_retry(message_id, delay_seconds=1)
        return
    message = db.get(Message, message_id)
    if not message or message.status in {MessageStatus.delivered, MessageStatus.read, MessageStatus.dead_lettered}:
        return

    start = time.perf_counter()
    attempt_number = message.retry_count + 1
    await asyncio.sleep(get_worker_delay_ms() / 1000)
    failed = random.random() < get_failure_rate() / 100
    latency_ms = round((time.perf_counter() - start) * 1000, 2)

    if failed:
        message.retry_count = attempt_number
        error = "Simulated downstream delivery failure"
        db.add(DeliveryAttempt(message_id=message.id, attempt_number=attempt_number, status="failed", error=error, latency_ms=latency_ms))
        if attempt_number >= get_settings().max_retries:
            _record_status(db, message, MessageStatus.dead_lettered, "message.failed", error)
            db.commit()
            await queue_service.publish_dead_letter(message.id)
            await websocket_manager.broadcast(message.room_id, {"type": "message.status", "message_id": message.id, "status": "dead_lettered", "retry_count": message.retry_count})
            return
        _record_status(db, message, MessageStatus.failed, "message.failed", error)
        db.commit()
        await queue_service.publish_retry(message.id, delay_seconds=min(2 ** attempt_number, 30))
        await websocket_manager.broadcast(message.room_id, {"type": "message.status", "message_id": message.id, "status": "failed", "retry_count": message.retry_count})
        return

    message.delivery_latency_ms = latency_ms
    db.add(DeliveryAttempt(message_id=message.id, attempt_number=attempt_number, status="delivered", latency_ms=latency_ms))
    _record_status(db, message, MessageStatus.delivered, "message.delivered")
    db.commit()
    db.refresh(message)
    await websocket_manager.broadcast(message.room_id, {"type": "message.delivered", "message": serialize_message(message)})


def mark_read(db: Session, message_id: str) -> Message:
    message = db.get(Message, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    _record_status(db, message, MessageStatus.read, "message.read")
    db.commit()
    db.refresh(message)
    return message


def list_messages(db: Session, room_id: str) -> list[Message]:
    return list(db.scalars(select(Message).where(Message.room_id == room_id).order_by(Message.sequence_number.asc())).all())


def count_messages(db: Session) -> int:
    return int(db.scalar(select(func.count(Message.id))) or 0)
