import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import SessionLocal, init_db
from app.routes.api import router
from app.services.messages import process_message
from app.services.queue import MAIN_QUEUE, RETRY_QUEUE, queue_service
from app.websocket.manager import websocket_manager


async def _local_queue_handler(payload: dict) -> None:
    with SessionLocal() as db:
        await process_message(db, payload["message_id"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    tasks: list[asyncio.Task] = []
    if get_settings().is_local:
        tasks = [
            asyncio.create_task(queue_service.consume_forever(_local_queue_handler, MAIN_QUEUE)),
            asyncio.create_task(queue_service.consume_forever(_local_queue_handler, RETRY_QUEUE)),
        ]
    try:
        yield
    finally:
        for task in tasks:
            task.cancel()
        for task in tasks:
            with suppress(asyncio.CancelledError):
                await task
        await queue_service.close()


app = FastAPI(title="QueuePulse API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[get_settings().frontend_origin, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.websocket("/ws/{room_id}/{username}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, username: str) -> None:
    await websocket_manager.connect(websocket, room_id, username)
    try:
        while True:
            payload = await websocket.receive_json()
            if payload.get("type") == "read":
                await websocket_manager.broadcast(room_id, {"type": "message.read", "message_id": payload.get("message_id"), "username": username})
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
