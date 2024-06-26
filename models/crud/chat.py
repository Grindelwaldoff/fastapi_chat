from typing import TypeVar, Generic, Type, Optional, List

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import Base
from models import ChatRoom, Message
from models.schemas import ChatRoomCreate, MessageCreate


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def create(self, obj_in: dict, session: AsyncSession) -> ModelType:
        instance = self.model(**obj_in)
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        return instance

    async def get_room_by_id(
        self, room_id: int, session: AsyncSession
    ) -> ModelType:
        obj = await session.execute(
            select(self.model).where(self.model.id == room_id)
        )
        return obj.scalars().first()

    async def get_room_by_cookie(self, cookie: str, session: AsyncSession):
        obj = await session.execute(
            select(self.model).where(self.model.user == cookie)
        )
        return obj.scalars().first()

    async def get_chatroom_message_history(
        self, session: AsyncSession, room_id: int
    ) -> Optional[ModelType]:
        objs = await session.execute(
            select(self.model).where(self.model.chat_room == room_id)
        )
        return objs.scalars().all()

    async def list_all(self, session: AsyncSession) -> List[ModelType]:
        objs = await session.execute(select(self.model))
        return objs.scalars().all()

    async def get_last_message(
        self, session: AsyncSession, room_id: int
    ):
        obj = await session.execute(
            select(self.model).where(self.model.chat_room == room_id)
        )
        return obj.scalars().first()

    async def delete(self, obj: ModelType, session: AsyncSession) -> ModelType:
        await session.delete(obj)
        await session.commit()
        return obj


chat_crud = CRUDBase[ChatRoom, ChatRoomCreate](ChatRoom)
message_crud = CRUDBase[Message, MessageCreate](Message)
