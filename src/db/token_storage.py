from abc import ABC, abstractmethod
from typing import Any, Optional

from redis.asyncio import Redis

from src.schemas.token import TokenType


class AsyncKeyValueStorage(ABC):
    @abstractmethod
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> None:
        pass

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        pass

    @abstractmethod
    async def add_user_token(
        self, user_id: str, token: str, token_type: TokenType, expire: int,
    ) -> None:
        pass

    @abstractmethod
    async def get_user_tokens(self, user_id: str, token_type: TokenType) -> set[bytes]:
        pass

    @abstractmethod
    async def blacklist_token(self, token: str, expire: int) -> None:
        pass

    @abstractmethod
    async def is_token_blacklisted(self, token: str) -> bool:
        pass


class RedisStorage(AsyncKeyValueStorage):
    """
    Redis storage implementation for managing tokens.

    Attributes:
        redis_client (Redis): The Redis client instance.
    """

    def __init__(self, redis_client: Redis):
        """
        Initialize the RedisStorage.

        Args:
            redis_client (Redis): The Redis client instance.
        """
        self.redis_client = redis_client
        if self.redis_client is None:
            raise ValueError('Redis client is required')

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> None:
        """
        Set a value in Redis with an optional expiration time.

        Args:
            key (str): The key under which the value is stored.
            value (Any): The value to store.
            expire (Optional[int]): The expiration time in seconds.
        """
        await self.redis_client.set(key, value, ex=expire)

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from Redis by key.

        Args:
            key (str): The key of the value to retrieve.

        Returns:
            Optional[Any]: The retrieved value or None if the key does not exist.
        """
        return await self.redis_client.get(key)

    async def delete(self, key: str) -> None:
        """
        Delete a value from Redis by key.

        Args:
            key (str): The key of the value to delete.
        """
        await self.redis_client.delete(key)

    async def add_user_token(
        self, user_id: str, token: str, token_type: TokenType, expire: int,
    ) -> None:
        """
        Add a user token to Redis with an expiration time.

        Args:
            user_id (str): The ID of the user.
            token (str): The token to store.
            token_type (TokenType): The type of the token (ACCESS or REFRESH).
            expire (int): The expiration time in seconds.
        """
        key = f"user:{user_id}:{token_type.value}_tokens"
        async with self.redis_client.pipeline() as pipe:
            await pipe.sadd(key, token)
            await pipe.expire(key, expire)
            await pipe.execute()

    async def get_user_tokens(self, user_id: str, token_type: TokenType) -> set[bytes]:
        """
        Get all tokens for a user from Redis.

        Args:
            user_id (str): The ID of the user.
            token_type (TokenType): The type of the tokens (ACCESS or REFRESH).

        Returns:
            Set[str]: A set of tokens.
        """
        key = f"user:{user_id}:{token_type.value}_tokens"
        return await self.redis_client.smembers(key)

    async def blacklist_token(self, token: str, expire: int) -> None:
        """
        Blacklist a token by adding it to Redis with an expiration time.

        Args:
            token (str): The token to blacklist.
            expire (int): The expiration time in seconds.
        """
        key = f"blacklist:{token}"
        await self.redis_client.set(key, 'revoked', ex=expire)

    async def is_token_blacklisted(self, token: str) -> bool:
        """
        Check if a token is blacklisted.

        Args:
            token (str): The token to check.

        Returns:
            bool: True if the token is blacklisted, False otherwise.
        """
        key = f"blacklist:{token}"
        return await self.redis_client.exists(key) == 1
