from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.entity import Chat
from fastapi.encoders import jsonable_encoder


class CustomChatService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_chats(self) -> list[Chat]:
        stmt = select(Chat)
        result = await self.db.execute(stmt)
        chats = result.scalars().all()
        return chats

    async def create_chat(self, new_chat) -> Chat:
        chat_dto = jsonable_encoder(new_chat)
        chat = Chat(**chat_dto)
        self.db.add(chat)
        await self.db.commit()
        return chat
