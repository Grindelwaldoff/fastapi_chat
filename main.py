import json
from datetime import datetime

from fastapi import (
    status,
    FastAPI,
    Depends,
    Request,
    APIRouter,
    WebSocket,
    HTTPException,
    WebSocketDisconnect,
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination, paginate, Page

from core.db import get_session
from core.config import settings
from models.crud.chat import chat_crud, message_crud
from models.schemas.chat import ChatRoomCreate, ChatRoomList, MessageBase
from utils.dependencies import (
    is_superuser,
    recognize_user,
    client_has_cookie,
    client_has_cookie_ws,
)
from utils.connection_manager import manager


app = FastAPI(title=settings.app_title)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


chat_router = APIRouter(prefix="/backend/chat", tags=["Чат"])


@chat_router.websocket(
    "/messages/{room_id}", dependencies=[Depends(client_has_cookie_ws)]
)
async def chat_room(
    room_id: int,
    websocket: WebSocket,
    user_data: dict = Depends(recognize_user),
    session: AsyncSession = Depends(get_session),
):
    await manager.connect(websocket, room_id)
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    try:
        while True:
            data = await websocket.receive_text()
            message = {
                "chat_room": int(room_id),
                "message": data,
                "admin_sender": user_data["is_admin"],
            }
            await message_crud.create(message, session)
            message.update({"time": current_time})
            await manager.broadcast(json.dumps(message), room_id, websocket)

    except WebSocketDisconnect:
        await manager.disconnect(room_id, websocket)


@chat_router.get(
    "/",
    dependencies=[Depends(client_has_cookie)],
)
async def list_chats(
    page: int = 1,
    size: int = 50,
    user_data: dict = Depends(is_superuser),
    session: AsyncSession = Depends(get_session),
) -> Page[ChatRoomList]:
    objs = await chat_crud.list_all(session)
    for obj in objs[(page - 1)*size:page*size]:
        obj.messages_count = len(
            await message_crud.get_chatroom_message_history(session, obj.id)
        )
        last_message = await message_crud.get_last_message(session, obj.id)
        if last_message:
            obj.last_message_time = last_message.created_date
    return paginate(objs)


@chat_router.post(
    "/",
    dependencies=[Depends(client_has_cookie)],
)
async def create_chat_room(
    request: Request, session: AsyncSession = Depends(get_session)
) -> ChatRoomCreate:
    cookie = request.cookies.get("sessionid")
    instance = await chat_crud.get_room_by_cookie(cookie, session)
    return instance if instance else await chat_crud.create(
        {"user": cookie}, session
    )


@chat_router.get(
    "/{room_id}",
    dependencies=[Depends(client_has_cookie)],
)
async def get_history(
    room_id: int,
    user_data: dict = Depends(recognize_user),
    session: AsyncSession = Depends(get_session),
) -> Page[MessageBase]:
    objs = await message_crud.get_chatroom_message_history(session, room_id)
    return paginate(objs)


@chat_router.delete(
    '/{room_id}',
    dependencies=[Depends(client_has_cookie)],
)
async def delete_chat_room(
    room_id: int,
    user_data: dict = Depends(is_superuser),
    session: AsyncSession = Depends(get_session),
) -> ChatRoomCreate:
    instance = await chat_crud.get_room_by_id(room_id, session)
    if instance:
        return await chat_crud.delete(instance, session)
    raise HTTPException(status.HTTP_200_OK)

add_pagination(app)
app.include_router(chat_router)
