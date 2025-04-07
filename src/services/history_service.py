from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from src.models.entity import Message
from collections.abc import Sequence


class CustomHistoryService:
    """
    Service for managing chat message history.

    This service provides methods to retrieve message history for a specific chat.
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the CustomHistoryService.

        Args:
            db (AsyncSession): The database session for interacting with the database.
        """
        self.db = db

    async def get_history(self, chat_id: UUID, limit: int, offset: int) -> Sequence[Message]:
        """
        Retrieve the message history for a specific chat.

        Args:
            chat_id (UUID): The ID of the chat for which to retrieve the message history.
            limit (int): The maximum number of messages to retrieve.
            offset (int): The number of messages to skip before starting to collect the result set.

        Returns:
            List[Message]: A list of messages for the specified chat.

        Raises:
            Exception: Raises an exception if there is an issue with the database query.
        """
        stmt = select(Message).where(Message.chat_id == chat_id).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        messages = result.scalars().all()
        return messages
