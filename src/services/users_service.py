import logging
import bcrypt

from uuid import UUID
from sqlalchemy.future import select
from src.models.entity import User
from src.schemas.entity import UserCreate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status


class CustomUserService:
    """
    Service for managing user-related operations, including user creation and retrieval.
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the CustomUserService.

        Args:
            db (AsyncSession): The database session for interacting with the database.
        """
        self.db = db

    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        Generate a hashed password using bcrypt.

        Args:
            password (str): The plain text password to hash.

        Returns:
            str: The hashed password.
        """
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        pwd_hash = bcrypt.hashpw(password=pwd_bytes, salt=salt).decode('utf-8')
        return pwd_hash

    @staticmethod
    def verify_password(hashed_password: str, provided_password: str) -> bool:
        """
        Verify a provided password against a hashed password.

        Args:
            hashed_password (str): The hashed password to verify against.
            provided_password (str): The plain text password to verify.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        pwd_bytes = provided_password.encode('utf-8')
        return bcrypt.checkpw(
            password=pwd_bytes,
            hashed_password=hashed_password.encode('utf-8'),
        )

    async def get_user(
        self,
        user_id: UUID = None,
        user_name: str = None,
    ) -> User:
        """
        Retrieve a user by user ID or username.

        Args:
            user_id (UUID, optional): The ID of the user to retrieve.
            user_name (str, optional): The username of the user to retrieve.

        Raises:
            HTTPException: If neither user_id nor user_name is provided, or if the user is not found.

        Returns:
            User: The retrieved user object.
        """
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

    async def create_user(self, new_user: UserCreate) -> User:
        """
        Create a new user in the database.

        Args:
            new_user (UserCreate): The user data to create a new user.

        Returns:
            User: The created user object.
        """
        user_dto = jsonable_encoder(new_user)
        user_dto.update(
            password=self.get_password_hash(new_user.password),
        )
        user = User(**user_dto)
        self.db.add(user)
        await self.db.commit()
        return user
