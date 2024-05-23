from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    Text,
    Boolean,
    DateTime
)

from core.db import Base


class ChatRoom(Base):
    __tablename__ = "chat_room"
    user = Column(String, unique=True, nullable=False)


class Message(Base):
    __tablename__ = "message"
    chat_room = Column(Integer, ForeignKey("chat_room.id"))
    message = Column(Text)
    admin_sender = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.now)
