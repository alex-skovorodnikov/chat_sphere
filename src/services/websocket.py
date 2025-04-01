from fastapi import WebSocket, WebSocketDisconnect
from fastapi import APIRouter
from typing import List
from models.entity import Message
from db.postgres import async_session
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.entity import MessageCreate

router = APIRouter()
active_connections: List[WebSocket] = []




