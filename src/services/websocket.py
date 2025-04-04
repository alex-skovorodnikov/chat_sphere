import logging
from uuid import UUID
from fastapi import Depends
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from schemas.entity import MessageCreate
from src.db.postgres import get_session
from src.depends.dependencies import (
    get_group_service,
    get_user_service,
    get_chat_service,
    get_message_service,
)
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
    message_service = get_message_service(db=db)

    new_message = await message_service.create_message(
        MessageCreate(chat_id=chat_id, sender_id=sender_id, text=text),
    )
    if not new_message:
        raise ValueError('Error creating message')
    logger.info(f'New message created {new_message=}')


@websocket_manager.handler('create_group')
async def create_group(
    title: str,
    creator_id: UUID,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    group_service = get_group_service(db=db)
    new_group = await group_service.create(GroupCreate(title=title, creator_id=creator_id))
    if not new_group:
        logger.error(f'Group with title {title} already exists')
    logger.info(f'New group created {new_group=}')


@websocket_manager.handler('add_user_to_group')
async def add_user_to_group(
    group_id: UUID,
    user_id: UUID,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    async with db.begin():
        group_service = get_group_service(db=db)
        user_service = get_user_service(db=db)

        group = await group_service.get_by_id(group_id)
        if not group:
            raise ValueError(f'Group with id {group_id} not found')

        user = await user_service.get_user(str(user_id))
        if not user:
            raise ValueError(f'User with id {user_id} not found')

        if user in group.users:
            raise ValueError(f'User {user_id} already in group {group_id}')

        group.users.append(user)
        await db.flush()
        await db.commit()
        logger.info(f'User added to group {group_id=} {user_id=}')


@websocket_manager.handler('create_chat')
async def create_chat(
    title: UUID,
    chat_type: Annotated[str, 'personal'],
    db: Annotated[AsyncSession, Depends(get_session)],
):
    async with db.begin():
        chat_service = get_chat_service(db=db)
        new_chat = await chat_service.create_chat(ChatCreate(title=str(title), chat_type=chat_type))
        if not new_chat:
            raise ValueError(f'Chat with title {title} already exists')
        logger.info(f'New chat created {new_chat=}')
