from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from src.models.entity import Message


class CustomHistoryService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_history(self, chat_id: UUID, limit: int, offset: int):
        stmt = select(Message).where(Message.chat_id == chat_id).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        messages = result.scalars().all()
        return messages
