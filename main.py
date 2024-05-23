import json
from typing import List
from datetime import datetime

from fastapi import (
    WebSocket,
    WebSocketDisconnect,
    FastAPI,
    Depends,
    HTTPException,
    Request,
)
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.db import get_session
from models.validators import (
    check_chat_room_exists,
    check_if_sender_is_admin,
    check_user_access,
)
from models.crud.chat import chat_crud, message_crud


app = FastAPI(title=settings.app_title, root_path="/backend/chat")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(
        self, message: dict, websocket: WebSocket, session: AsyncSession
    ):
        # сохранение сообщения в бд
        await websocket.send_text(json.dumps(message))

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


def admin_or_room_owner(websocket: WebSocket):
    session_id = websocket.cookies.get("sessionid")
    if not session_id:
        raise HTTPException(status_code=401)
    return True


@app.websocket("/messages/{room_id}")
async def chat_room(
    room_id: str,
    websocket: WebSocket,
    session: AsyncSession = Depends(get_session),
):
    # проверка, что пользователь владелец комнаты
    cookie = websocket.cookies.get("sessionid")
    await check_user_access(cookie, session)
    await manager.connect(websocket)
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    try:
        while True:
            data = await websocket.receive_text()
            message = {
                "chat_room": room_id,
                "message": data,
                "admin_sender": await check_if_sender_is_admin(
                    room_id, cookie, session
                ),
            }
            await message_crud.create(message, session)
            await manager.send_personal_message(message, websocket, session)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        message = {
            "time": current_time,
            "room_id": room_id,
            "message": "Offline",
        }
        await manager.broadcast(json.dumps(message))


@app.post("/")
async def create_chat_room(
    request: Request, session: AsyncSession = Depends(get_session)
):
    cookie = request.cookies.get("sessionid")
    await check_chat_room_exists(cookie, session)
    return await chat_crud.create({"user": cookie}, session)


@app.get("/{room_id}")
async def get_history(
    room_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    return await message_crud.get_chatroom_message_history(session, room_id)
