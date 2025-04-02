from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.encoders import jsonable_encoder
from src.models.entity import Group


class CustomGroupService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self):
        stmt = select(Group)
        result = await self.db.execute(stmt)
        groups = result.scalars().all()
        return groups

    async def create(self, new_group):
        group_dto = jsonable_encoder(new_group)
        group = Group(**group_dto)
        self.db.add(group)
        await self.db.commit()
        return group
