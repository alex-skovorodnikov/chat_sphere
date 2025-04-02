from fastapi import WebSocket


class WebSocketConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[tuple[str, WebSocket]]] = {}

    async def connect(self, chat_id: str, user_id: str, websocket: WebSocket):
        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = []
        await websocket.accept()
        self.active_connections[chat_id].append((user_id, websocket))

    async def disconnect(self, chat_id: str, websocket: WebSocket):
        self.active_connections[chat_id] = [
            (uid, conn) for uid, conn in self.active_connections[chat_id] if conn != websocket
        ]
        if not self.active_connections[chat_id]:
            del self.active_connections[chat_id]

    async def send_message(self, chat_id: str, message: str):
        if chat_id in self.active_connections:
            for user_id, connection in self.active_connections[chat_id]:
                await connection.send_text(message)
