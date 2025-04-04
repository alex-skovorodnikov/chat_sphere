import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, set[WebSocket]] = {}
        self.handlers: dict[str, callable] = {}

    def handler(self, action):
        def wrapper(func):
            self.handlers[action] = func
            return func
        return wrapper

    async def connect(self, user_id: str, websocket: WebSocket):
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        await websocket.accept()
        self.active_connections[user_id].add(websocket)
        logger.info(f"Connect for {user_id=} conntections: {len(self.active_connections[user_id])}")

    async def disconnect(self, user_id: str, websocket: WebSocket):
        self.active_connections[user_id].remove(websocket)
        logger.info(f"DisConnect for {user_id=} conntections: {len(self.active_connections[user_id])}")

        if not self.active_connections[user_id]:
            del self.active_connections[user_id]

    async def send_message(self, user_id: str, message: str):
        if user_id in self.active_connections:
            for websocket in self.active_connections[user_id]:
                await websocket.send_text(message)
                logger.info(f"Send message {message} for {websocket=}.")
