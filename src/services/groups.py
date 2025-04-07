import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi.encoders import jsonable_encoder
from src.models.entity import Group, User
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

    async def create(self, new_group, user: User):
        group_dto = jsonable_encoder(new_group)
        group = Group(**group_dto)
        try:
            self.db.add(group)
            await self.db.commit()
            # await self.add_user_to_group(user=user, group=group)
        except IntegrityError:
            # await self.db.rollback()
            logger.debug(f"Group with title '{new_group.title}' already exists.")
            return
        return group

    async def add_user_to_group(self, user: User, group: Group):
        try:
            group.users.append(user)
            await self.db.flush()
            await self.db.commit()
            logger.debug(f'User added to group {group.id=} {user.id=}')
        except IntegrityError:
            await self.db.rollback()
            logger.debug(f"User '{user.id}' already in group '{group.id}'.")
            return
