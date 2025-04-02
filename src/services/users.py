import logging
import bcrypt

from sqlalchemy.future import select
from src.models.entity import User
from src.schemas.entity import UserCreate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status


class CustomUserService():

    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def get_password_hash(password: str) -> str:
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        pwd_hash = bcrypt.hashpw(password=pwd_bytes, salt=salt).decode('utf-8')
        return pwd_hash

    @staticmethod
    def verify_password(hashed_password: str, provided_password: str) -> bool:
        pwd_bytes = provided_password.encode('utf-8')
        return bcrypt.checkpw(
            password=pwd_bytes,
            hashed_password=hashed_password.encode('utf-8'),
        )

    async def get_users(self) -> list[User]:
        stmt = select(User)
        result = await self.db.execute(stmt)
        users = result.scalars().all()
        return users

    async def get_user(
        self,
        user_id: str = None,
        user_name: str = None,
    ) -> User:
        if not user_id and not user_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='user_id or username must be provided',
            )

        if user_id:
            stmt = select(User).where(User.id == user_id)
        else:
            stmt = select(User).where(User.name == user_name)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            logging.warning(f"User not found with user_name: {user_name}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found',
            )
        return user

    async def create_user(self, new_user: UserCreate):
        user_dto = jsonable_encoder(new_user)
        user_dto.update(
            password=self.get_password_hash(new_user.password),
        )
        user = User(**user_dto)
        self.db.add(user)
        await self.db.commit()
        return user
