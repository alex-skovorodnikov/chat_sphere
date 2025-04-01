from fastapi import WebSocket, WebSocketDisconnect
from fastapi import APIRouter
from typing import List
from models.entity import Message
from db.postgres import async_session
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.entity import MessageCreate
from uuid import UUID, uuid4

router = APIRouter()
active_connections: List[WebSocket] = []

@router.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            print(f'{data=}')
    except WebSocketDisconnect:
        active_connections.remove(websocket)

@router.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str):
    await websocket.accept()
    active_connections.append(websocket)

    try:
        async with async_session() as session:
            while True:
                data = await websocket.receive_text()
                message = MessageCreate(chat_id=UUID(chat_id), sender_id=uuid4(), text=data)
                await session.add(message)
                await session.commit()
                for connection in active_connections:
                    # if connection.client_state == WebSocketState.OPEN:
                    await connection.send_text(data)

    except WebSocketDisconnect:
        active_connections.remove(websocket)