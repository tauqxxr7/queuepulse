from collections import defaultdict
from typing import Any

from fastapi import WebSocket

from app.services.cache import cache_service


class WebSocketManager:
    def __init__(self) -> None:
        self._rooms: dict[str, set[WebSocket]] = defaultdict(set)
        self._meta: dict[WebSocket, tuple[str, str]] = {}

    async def connect(self, websocket: WebSocket, room_id: str, username: str) -> None:
        await websocket.accept()
        self._rooms[room_id].add(websocket)
        self._meta[websocket] = (room_id, username)
        cache_service.mark_online(username, room_id)
        await self.broadcast(room_id, {"type": "presence.joined", "username": username})

    def disconnect(self, websocket: WebSocket) -> None:
        meta = self._meta.pop(websocket, None)
        if not meta:
            return
        room_id, username = meta
        self._rooms[room_id].discard(websocket)
        cache_service.mark_offline(username, room_id)

    async def broadcast(self, room_id: str, payload: dict[str, Any]) -> None:
        stale: list[WebSocket] = []
        for websocket in list(self._rooms[room_id]):
            try:
                await websocket.send_json(payload)
            except Exception:
                stale.append(websocket)
        for websocket in stale:
            self.disconnect(websocket)


websocket_manager = WebSocketManager()
