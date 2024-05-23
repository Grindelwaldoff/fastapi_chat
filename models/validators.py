from fastapi import WebSocketException, status, HTTPException
from sqlalchemy.sql import text
from sqlalchemy.ext.asyncio import AsyncSession

from models.crud.chat import chat_crud


async def check_chat_room_exists(cookie: str, session: AsyncSession) -> None:
    instance = await chat_crud.get_room_by_cookie(cookie, session)
    if instance:
        raise HTTPException(
            status.HTTP_405_METHOD_NOT_ALLOWED,
            detail=(
                f"Чат с этим пользователем уже существует, id - {instance.id}"
            ),
        )


async def check_if_sender_is_admin(
    room_id: str, cookie: str, session: AsyncSession
) -> bool:
    obj = await chat_crud.get_room_by_cookie(cookie, session)
    if obj.id == int(room_id):
        return obj is None
    raise HTTPException(status.HTTP_403_FORBIDDEN)


async def check_user_access(cookie: str, session: AsyncSession):
    obj = await session.execute(
        text(f'SELECT * FROM django_session WHERE session_key = "{cookie}"')
    )
    chat_room = await chat_crud.get_room_by_cookie(cookie, session)
    if obj.scalars().first() is None and chat_room is None:
        raise WebSocketException(status.HTTP_403_FORBIDDEN)
    return True
