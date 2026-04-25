from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import init_db
from app.routes.api import router
from app.websocket.manager import websocket_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


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
