from fastapi import (
    status,
    Request,
    Depends,
    WebSocket,
    HTTPException,
    WebSocketException,
)
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_session
from models.crud.chat import chat_crud


def client_has_cookie(request: Request):
    if "sessionid" in request.cookies:
        return True
    raise HTTPException(status.HTTP_400_BAD_REQUEST)


def client_has_cookie_ws(websocket: WebSocket):
    if "sessionid" in websocket.cookies:
        return True
    raise WebSocketException(status.HTTP_400_BAD_REQUEST)


async def get_user_instance(
    protocol: Request | WebSocket,
    session: AsyncSession,
    room_id: int,
    is_admin: bool = False
) -> dict[str, str | bool]:
    cookie = protocol.cookies.get('sessionid')
    result = {'cookie': cookie, 'is_admin': is_admin}
    obj = await session.execute(
        text(f"SELECT * FROM django_session WHERE session_key = '{cookie}'")
    )
    obj = obj.scalars().first()
    if obj:
        result.update({'is_admin': True})
        return result
    chat_room = await chat_crud.get_room_by_cookie(cookie, session)
    if obj is None and (chat_room is None or chat_room.id != room_id):
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    return result


async def is_superuser(
    room_id: int = None,
    request: Request = None,
    session: AsyncSession = Depends(get_session),
):
    user_data = await get_user_instance(request, session, room_id)
    if not user_data['is_admin']:
        raise HTTPException(status.HTTP_403_FORBIDDEN)
    return user_data


async def recognize_user(
    room_id: int = None,
    request: Request = None,
    websocket: WebSocket = None,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str | bool]:
    protocol = request if request else websocket
    return await get_user_instance(protocol, session, room_id)
