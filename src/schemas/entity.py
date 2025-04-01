from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class User(BaseModel):
    id: UUID
    name: str
    email: str

    class Config:
        from_attributes = True


class GroupCreate(BaseModel):
    title: str


class Group(BaseModel):
    id: UUID
    title: str
    users: list[User] = []

    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    chat_id: UUID
    sender_id: UUID
    text: str


class MessageCreate(MessageBase):
    pass


class Message(MessageBase):
    id: UUID
    timestamp: datetime
    is_read: bool = False

    class Config:
        from_attributes = True
