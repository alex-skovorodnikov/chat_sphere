from fastapi.encoders import jsonable_encoder

from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.entity import MessageCreate
from src.models.entity import Message


class CustomMessageService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_message(self, new_message: MessageCreate):
        message_dto = jsonable_encoder(new_message)
        message = Message(**message_dto)
        self.db.add(message)
        await self.db.commit()
        return message
