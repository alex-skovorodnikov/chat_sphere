from fastapi import APIRouter, WebSocket

router = APIRouter()
active_connections: list[WebSocket] = []
