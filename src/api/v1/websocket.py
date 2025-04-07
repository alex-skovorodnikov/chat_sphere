import logging
from typing import Annotated
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from src.depends.dependencies import (
    get_current_user,
    get_token,
)
from src.services.websocket import websocket_manager
from src.db.postgres import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from json.decoder import JSONDecodeError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket('')
async def websocket_endpoint(
    websocket: WebSocket,
    token: Annotated[str, Depends(get_token)],
    db: Annotated[AsyncSession, Depends(get_session)],
):
    user_id = get_current_user(token)

    await websocket_manager.connect(user_id, websocket)
    try:
        while True:
            try:
                data = await websocket.receive_json()

                action = data.get('type')
                if not action:
                    logger.error('No type in message')
                    await websocket.send_text('No type in message')
                    continue

                handler = websocket_manager.handlers.get(action)

                if not handler:
                    logger.error(f'No handler for type: {action}')
                    await websocket.send_text('No handler for this action')
                    continue

                payload = data.get('payload')
                logger.info(f'Got payload: {payload=}')
                if not payload:
                    logger.error('No payload in message')
                    await websocket.send_text('No payload in message')
                    continue
                payload['user_id'] = user_id
                logger.info(f'New payload: {payload=}')
                await handler(**payload, db=db)

            except (JSONDecodeError, AttributeError) as e:
                logger.error(f'Error receiving message: {e}')
                await websocket.send_text('Wrong message format')
                continue
            except ValueError as e:
                logger.error(f'Value error : {e}')
                await websocket.send_text(f'Value error: {e}')
                continue

            await websocket_manager.send_message(user_id, f'resp: {data}', websocket)
    except WebSocketDisconnect:
        await websocket_manager.disconnect(user_id, websocket)
