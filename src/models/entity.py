from datetime import datetime

from sqlalchemy import (
    Boolean, CheckConstraint, Column, DateTime, ForeignKey,
    String, Table,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.db.postgres import Base

group_users = Table(
    'group_users',
    Base.metadata,
    Column('group_id', UUID, ForeignKey('groups.id')),
    Column('user_id', UUID, ForeignKey('users.id')),
)


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        server_default=func.uuid_generate_v4(),
    )
    name: Mapped[str] = mapped_column(String, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password: Mapped[str] = mapped_column(String)

    groups = relationship('Group', secondary=group_users, back_populates='users')


class Chat(Base):
    __tablename__ = 'chats'
    __table_args__ = {'extend_existing': True}

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        server_default=func.uuid_generate_v4(),
    )
    title: Mapped[str] = mapped_column(String, index=True)
    chat_type: Mapped[str] = mapped_column(String, nullable=False)

    __table_args__ = (
        CheckConstraint("chat_type IN ('personal', 'group')", name='check_chat_type'),
    )


class Group(Base):
    __tablename__ = 'groups'
    __table_args__ = {'extend_existing': True}

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        server_default=func.uuid_generate_v4(),
    )
    title: Mapped[str] = mapped_column(String, index=True)
    creator_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('users.id'))
    creator: Mapped[User] = relationship('User')

    users = relationship('User', secondary=group_users, back_populates='groups')


class Message(Base):
    __tablename__ = 'messages'
    __table_args__ = {'extend_existing': True}

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        server_default=func.uuid_generate_v4(),
    )
    chat_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('chats.id'))
    sender_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'))
    text: Mapped[str] = mapped_column(String, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
