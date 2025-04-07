import logging
from uuid import UUID
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.entity import User, Group, Chat, Message

from schemas.entity import MessageCreate
from src.db.postgres import get_session
from src.schemas.entity import GroupCreate, ChatCreate

from src.managers.websocket_manager import WebSocketConnectionManager

logger = logging.getLogger(__name__)

websocket_manager = WebSocketConnectionManager()


@websocket_manager.handler('new_message')
async def new_message(
    chat_id: UUID,
    sender_id: UUID,
    text: str,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    try:
        message = MessageCreate(chat_id=chat_id, sender_id=sender_id, text=text)
        message_dto = jsonable_encoder(message.model_dump())
        message = Message(**message_dto)

        db.add(message)
        await db.commit()

    except Exception as e:
        raise ValueError(f'Error creating message. {e}')
    logger.info(f'New message created {new_message=}')


@websocket_manager.handler('add_user_to_group')
async def add_user_to_group(
    group_id: UUID,
    user_id: UUID,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    async with (db.begin()):

        stmt = select(Group).where(Group.id == user_id)
        res = await db.execute(stmt)
        group = res.scalar_one_or_none()
        if not group:
            raise ValueError(f'Group with id {group_id} not found')

        stmt = select(User).where(User.id == user_id)
        res = await db.execute(stmt)
        user = res.scalar_one_or_none()
        if not user:
            raise ValueError(f'User with id {user_id} not found')

        if user in group.users:
            raise ValueError(f'User {user_id} already in group {group_id}')

        group.users.append(user)
        await db.commit()
        logger.info(f'{user_id=} added to group {group_id=} ')


@websocket_manager.handler('create_group_chat')
async def create_group_chat(
    chat_title: str,
    group_title: str,
    creator_id: UUID,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    logger.info(f'Creating group chat {chat_title} {group_title}')
    try:
        async with db.begin():
            stmt = select(User).where(User.id == creator_id)
            res = await db.execute(stmt)
            user = res.scalar_one_or_none()

            group_dto = jsonable_encoder(GroupCreate(title=group_title, creator_id=creator_id).model_dump())
            new_group = Group(**group_dto)
            db.add(new_group)
            new_group.users.append(user)
            await db.flush()

            chat_dto = jsonable_encoder(
                ChatCreate(
                    title=chat_title,
                    chat_type='group',
                    group_id=new_group.id,
                ).model_dump(),
            )
            new_chat = Chat(**chat_dto)
            db.add(new_chat)
            await db.commit()

    except Exception as e:
        logger.error(f'An error occurred while creating chat with title {chat_title}. {e}')
        raise ValueError(f'An error occurred while creating chat with title {chat_title}. {e}')


@websocket_manager.handler('create_personal_chat')
async def create_personal_chat(
    creator_id: UUID,
    other_user_id: UUID,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    logger.info(f'Creating personal chat {creator_id} {other_user_id}')
    try:
        async with db.begin():
            stmt = select(User).where(User.id == creator_id)
            res = await db.execute(stmt)
            user = res.scalar_one_or_none()

            stmt = select(User).where(User.id == other_user_id)
            res = await db.execute(stmt)
            other_user = res.scalar_one_or_none()

            if not other_user:
                raise ValueError('Not found other user {other_user_id=}')

            new_group = Group(
                title=f'{user.name}_{other_user.name}',
                creator_id=creator_id,
                users=[user, other_user],
            )
            db.add(new_group)
            await db.flush()

            chat_dto = jsonable_encoder(
                ChatCreate(
                    title=f'Chat between {user.name} and {other_user.name}',
                    chat_type='personal',
                    group_id=new_group.id,
                ).model_dump(),
            )
            new_chat = Chat(**chat_dto)
            db.add(new_chat)
            await db.commit()
    except Exception as e:
        logger.error(f'An error occurred while creating personal chat with user_id '
                     f'{creator_id} and other_user_id {other_user_id} {e}')
        raise ValueError(f'An error occurred while creating personal chat with user_id '
                         f'{creator_id} and other_user_id {other_user_id} {e}')
