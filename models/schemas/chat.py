from pydantic import BaseModel, Field


class ChatRoomBase(BaseModel):
    user: str = Field(None, min_length=1)


class ChatRoomCreate(ChatRoomBase):
    user: str = Field(min_length=1)


class MessageBase(BaseModel):
    chat_room: int = Field(None, gt=0)
    message: str = Field(None, min_length=1)
    admin_sender: bool = Field(None)


class MessageCreate(MessageBase):
    chat_room: int = Field(gt=0)
    message: str = Field(min_length=1)
    admin_sender: bool = Field(...)
