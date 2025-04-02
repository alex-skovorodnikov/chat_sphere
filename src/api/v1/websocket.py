import logging
from typing import Annotated
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from src.depends.dependencies import get_current_user, get_websocket_manager, get_message_service
from src.services.websocket import WebSocketConnectionManager
from src.services.messages import CustomMessageService
from src.schemas.entity import MessageCreate


logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket('/{chat_id}')
async def websocket_endpoint(
        websocket: WebSocket,
        chat_id: str,
        manager: Annotated[WebSocketConnectionManager, Depends(get_websocket_manager)],
        message_service: Annotated[CustomMessageService, Depends(get_message_service)],

):
    token = websocket.query_params.get('token')
    user_id = get_current_user(token)
    logger.info(f'{token=} {user_id=} success')

    await manager.connect(chat_id, user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = MessageCreate(
                chat_id=chat_id,
                sender_id=user_id,
                text=data,
            )
            await message_service.create_message(message)
            await manager.send_message(chat_id, f'Message from {user_id} in chat {chat_id}: {data}')
    except WebSocketDisconnect:
        await manager.disconnect(chat_id, websocket)
