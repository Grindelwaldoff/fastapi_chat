from datetime import datetime

from pydantic import BaseModel, Field


class ChatRoomBase(BaseModel):
    id: int = Field(None)
    user: str = Field(None, min_length=1)


class ChatRoomCreate(ChatRoomBase):
    user: str = Field(min_length=1)


class ChatRoomList(ChatRoomBase):
    user: str = Field(min_length=1)
    messages_count: int
    last_message_time: datetime = Field(None)


class MessageBase(BaseModel):
    chat_room: int = Field(None, gt=0)
    message: str = Field(None, min_length=1)
    admin_sender: bool = Field(None)


class MessageCreate(MessageBase):
    chat_room: int = Field(gt=0)
    message: str = Field(min_length=1)
    admin_sender: bool = Field(...)
