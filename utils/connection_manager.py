from typing import List, Dict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    async def disconnect(
        self, room_id: str, websocket: WebSocket,
    ):
        self.active_connections[room_id].remove(websocket)

    async def broadcast(
        self, message: str, room_id: str, websocket: WebSocket
    ):
        for connection in self.active_connections[room_id]:
            if connection != websocket:
                await connection.send_text(message)


manager = ConnectionManager()
