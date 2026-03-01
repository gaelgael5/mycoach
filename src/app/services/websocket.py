"""WebSocket connection manager with heartbeat."""
import asyncio
import json
import logging
import uuid
from fastapi import WebSocket

logger = logging.getLogger("mycoach.ws")


class ConnectionManager:
    """Manages WebSocket connections per conversation."""

    def __init__(self):
        # conversation_id -> set of WebSocket connections
        self._connections: dict[uuid.UUID, set[WebSocket]] = {}
        self._heartbeat_tasks: dict[WebSocket, asyncio.Task] = {}

    async def connect(self, conversation_id: uuid.UUID, ws: WebSocket):
        await ws.accept()
        self._connections.setdefault(conversation_id, set()).add(ws)
        # Start heartbeat
        task = asyncio.create_task(self._heartbeat(ws))
        self._heartbeat_tasks[ws] = task
        logger.info("WS connected: conversation=%s", conversation_id)

    def disconnect(self, conversation_id: uuid.UUID, ws: WebSocket):
        conns = self._connections.get(conversation_id)
        if conns:
            conns.discard(ws)
            if not conns:
                del self._connections[conversation_id]
        task = self._heartbeat_tasks.pop(ws, None)
        if task:
            task.cancel()
        logger.info("WS disconnected: conversation=%s", conversation_id)

    async def broadcast(self, conversation_id: uuid.UUID, data: dict):
        conns = self._connections.get(conversation_id, set()).copy()
        payload = json.dumps(data, default=str)
        for ws in conns:
            try:
                await ws.send_text(payload)
            except Exception:
                self.disconnect(conversation_id, ws)

    async def _heartbeat(self, ws: WebSocket):
        """Send ping every 30s."""
        try:
            while True:
                await asyncio.sleep(30)
                try:
                    await ws.send_json({"type": "ping"})
                except Exception:
                    break
        except asyncio.CancelledError:
            pass


manager = ConnectionManager()
