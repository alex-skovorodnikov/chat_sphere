from uuid import UUID, uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from db.postgres import async_session
from schemas.entity import MessageCreate

router = APIRouter()
active_connections: list[WebSocket] = []


@router.websocket('/ws/{chat_id}')
async def websocket_endpoint(websocket: WebSocket, chat_id: str):
    await websocket.accept()
    active_connections.append(websocket)

    try:
        async with async_session() as session:
            while True:
                data = await websocket.receive_text()
                message = MessageCreate(
                    chat_id=UUID(chat_id), sender_id=uuid4(), text=data,
                )
                await session.add(message)
                await session.commit()
                for connection in active_connections:
                    # if connection.client_state == WebSocketState.OPEN:
                    await connection.send_text(data)

    except WebSocketDisconnect:
        active_connections.remove(websocket)
