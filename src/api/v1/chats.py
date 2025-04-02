from fastapi import APIRouter, Depends

from services.chats import CustomChatService
from src.schemas.entity import Chat, ChatCreate
from typing import Annotated
from src.depends.dependencies import get_chat_service

router = APIRouter()


@router.get(
    '',
    response_model=list[Chat],
    summary='Get all chats',
    description='Return all existing chats',
    responses={200: {'description': 'List of chats'}},
)
async def get_chats(
    chat_servie: Annotated[CustomChatService, Depends(get_chat_service)],
) -> list[Chat]:
    return await chat_servie.get_all_chats()


@router.post(
    '',
    response_model=Chat,
    summary='Create a new chat',
    description='Create a new chat in the system',
    responses={200: {'description': 'The created chat'}},
)
async def create_chat(
    new_chat: ChatCreate,
    chat_service: Annotated[CustomChatService, Depends(get_chat_service)],
):
    chat = await chat_service.create_chat(new_chat)
    return chat
