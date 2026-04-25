from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class RoomCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class RoomOut(BaseModel):
    id: str
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    room_id: str
    username: str = Field(min_length=1, max_length=80)
    content: str = Field(min_length=1, max_length=4000)
    client_message_id: str = Field(min_length=1, max_length=120)


class MessageOut(BaseModel):
    id: str
    room_id: str
    user_id: str
    username: str
    client_message_id: str
    content: str
    sequence_number: int
    status: str
    retry_count: int
    failure_reason: str | None
    delivery_latency_ms: float | None
    created_at: datetime


class SimulationSettings(BaseModel):
    failure_rate: float = Field(ge=0, le=100)


class WorkerDelaySettings(BaseModel):
    worker_delay_ms: int = Field(ge=0, le=10000)


class LoadSpikeRequest(BaseModel):
    room_id: str
    username_prefix: str = "load-user"
    messages: int = Field(default=100, ge=1, le=5000)


class MetricsOut(BaseModel):
    total_messages: int
    messages_per_second: float
    queue_depth: int
    retry_queue_count: int
    dead_letter_count: int
    active_users: int
    active_rooms: int
    success_rate: float
    average_delivery_latency_ms: float
    failure_rate: float
    recent_failed_messages: list[dict[str, Any]]
    throughput_series: list[dict[str, Any]]
    latency_series: list[dict[str, Any]]
    queue_depth_series: list[dict[str, Any]]
    success_failed: list[dict[str, Any]]
