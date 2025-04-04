import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi.encoders import jsonable_encoder
from src.models.entity import Group
from uuid import UUID

logger = logging.getLogger(__name__)


class CustomGroupService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self):
        stmt = select(Group).options(selectinload(Group.users))
        result = await self.db.execute(stmt)
        groups = result.scalars().all()
        return groups

    async def get_by_id(self, group_id: UUID):
        stmt = select(Group).where(Group.id == group_id).options(selectinload(Group.users))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, new_group):
        group_dto = jsonable_encoder(new_group)
        group = Group(**group_dto)
        self.db.add(group)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            logger.warning(f"Group with title '{new_group.title}' already exists.")
            return
        return group
