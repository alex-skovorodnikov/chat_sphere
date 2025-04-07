import logging

from fastapi import APIRouter, Depends, Path
from typing import Annotated
from uuid import UUID
from src.schemas.entity import Message
from src.depends.dependencies import CustomHistoryService, get_history_service
from src.depends.dependencies import get_pagination_params


logger = logging.getLogger(__name__)


router = APIRouter()


@router.get(
    '/history/{chat_id}',
    summary='Get chat history',
    description='Get messages in the chat',
    response_model=list[Message],
)
async def get_chat_history(
    pagination: Annotated[tuple[int, int], Depends(get_pagination_params)],
    history_service: Annotated[CustomHistoryService, Depends(get_history_service)],
    chat_id: Annotated[UUID, Path()],
):
    logger.info(f'Get chat history for chat_id: {chat_id}')
    limit, offset = pagination
    messages = await history_service.get_history(chat_id=chat_id, limit=limit, offset=offset)
    return messages
