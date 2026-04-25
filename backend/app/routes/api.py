import asyncio
from uuid import uuid4

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.metrics.collector import collect_metrics, generate_insights
from app.models.entities import Room
from app.schemas import LoadSpikeRequest, MessageCreate, MessageOut, MetricsOut, RoomCreate, RoomOut, SimulationSettings, WorkerDelaySettings
from app.services.messages import create_room, list_messages, serialize_message, submit_message
from app.services.state import set_consumer_paused, set_failure_rate as set_runtime_failure_rate, set_worker_delay_ms

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "queuepulse"}


@router.post("/api/rooms", response_model=RoomOut)
def create_room_endpoint(payload: RoomCreate, db: Session = Depends(get_db)) -> Room:
    return create_room(db, payload.name)


@router.get("/api/rooms", response_model=list[RoomOut])
def list_rooms(db: Session = Depends(get_db)) -> list[Room]:
    return db.query(Room).order_by(Room.created_at.desc()).all()


@router.post("/api/messages", response_model=MessageOut)
async def create_message(payload: MessageCreate, db: Session = Depends(get_db)) -> dict:
    message = await submit_message(db, payload)
    db.refresh(message)
    return serialize_message(message)


@router.get("/api/messages/{room_id}", response_model=list[MessageOut])
def messages(room_id: str, db: Session = Depends(get_db)) -> list[dict]:
    return [serialize_message(message) for message in list_messages(db, room_id)]


@router.get("/api/metrics", response_model=MetricsOut)
def metrics(db: Session = Depends(get_db)) -> dict:
    return collect_metrics(db)


@router.get("/api/insights")
def insights(db: Session = Depends(get_db)) -> dict:
    metrics_payload = collect_metrics(db)
    return {"insights": generate_insights(metrics_payload), "metrics": metrics_payload}


@router.post("/api/simulate/failure-rate")
def set_failure_rate(payload: SimulationSettings) -> dict:
    return {"failure_rate": set_runtime_failure_rate(payload.failure_rate)}


@router.post("/api/simulate/worker-delay")
def set_worker_delay(payload: WorkerDelaySettings) -> dict:
    return {"worker_delay_ms": set_worker_delay_ms(payload.worker_delay_ms)}


@router.post("/api/simulate/load-spike")
async def load_spike(payload: LoadSpikeRequest, db: Session = Depends(get_db)) -> dict:
    created = 0
    for idx in range(payload.messages):
        await submit_message(
            db,
            MessageCreate(
                room_id=payload.room_id,
                username=f"{payload.username_prefix}-{idx % 25}",
                content=f"load spike message {idx}",
                client_message_id=f"load-{uuid4()}",
            ),
        )
        created += 1
        if idx % 100 == 0:
            await asyncio.sleep(0)
    return {"created": created}


@router.post("/api/simulate/consumer-pause")
def consumer_pause() -> dict:
    set_consumer_paused(True)
    return {"consumer_paused": True}


@router.post("/api/simulate/consumer-resume")
def consumer_resume() -> dict:
    set_consumer_paused(False)
    return {"consumer_paused": False}
