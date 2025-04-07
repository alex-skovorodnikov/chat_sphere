import logging
from fastapi import WebSocket
from uuid import UUID
from typing import Callable

logger = logging.getLogger(__name__)


class WebSocketConnectionManager:
    """
    Manager for handling WebSocket connections.

    This class manages active WebSocket connections for users,
    allowing them to connect, disconnect, and send messages.
    """

    def __init__(self) -> None:
        """
        Initialize the connection manager.

        Creates a dictionary to store active connections and a dictionary for
        storing action handlers.
        """
        self.active_connections: dict[UUID, set[WebSocket]] = {}
        self.handlers: dict[str, Callable] = {}

    def handler(self, action: str) -> Callable:
        """
        Decorator for registering action handlers.

        Args:
            action (str): The name of the action for which the handler is registered.

        Returns:
            Callable: The wrapped handler function.
        """
        def wrapper(func: Callable) -> Callable:
            self.handlers[action] = func
            return func
        return wrapper

    async def connect(self, user_id: UUID, websocket: WebSocket) -> None:
        """
        Establish a WebSocket connection for a user.

        Args:
            user_id (UUID): The user's identifier.
            websocket (WebSocket): The WebSocket object for the connection.
        """
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        await websocket.accept()
        self.active_connections[user_id].add(websocket)
        logger.debug(f"Connect for {user_id=} connections: {len(self.active_connections[user_id])}")

    async def disconnect(self, user_id: UUID, websocket: WebSocket) -> None:
        """
        Disconnect a WebSocket connection for a user.

        Args:
            user_id (UUID): The user's identifier.
            websocket (WebSocket): The WebSocket object for the disconnection.
        """
        self.active_connections[user_id].remove(websocket)
        logger.info(f"Disconnect for {user_id=} connections: {len(self.active_connections[user_id])}")

        if not self.active_connections[user_id]:
            del self.active_connections[user_id]

    async def send_message(self, user_id: UUID, message: str, current_websocket: WebSocket) -> None:
        """
        Send a message to all connected WebSockets except the current one.

        Args:
            user_id (UUID): The user's identifier.
            message (str): The message to send.
            current_websocket (WebSocket): The current WebSocket that should not receive the message.
        """
        if user_id in self.active_connections:
            for websocket in self.active_connections[user_id]:
                if websocket != current_websocket:
                    await websocket.send_text(message)
                    logger.info(f"Send message {message} for {websocket=}.")
