import datetime
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Optional, Any

import jwt

from src.db.token_storage import AsyncKeyValueStorage
from src.schemas.entity import User
from src.schemas.token import TOKEN_TYPE_FIELD, TokenType, TokenInfo

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the logging level as needed


class TokenManageService(ABC):
    """
    Abstract base class for token management services.
    """

    @abstractmethod
    def create_token(self, data: dict, expire: int, token_type: TokenType) -> str:
        """
        Create a token with the given data, expiration time, and token type.

        :param data: The data to include in the token payload.
        :param expire: The expiration time in minutes.
        :param token_type: The type of the token.
        :return: The encoded token as a string.
        """
        pass

    @abstractmethod
    async def validate_token(self, token: str, token_type: TokenType) -> dict:
        """
        Validate the given token and return its payload.

        :param token: The token to validate.
        :param token_type: The type of the token.
        :return: The decoded token payload as a dictionary.
        """
        pass

    @abstractmethod
    async def revoke_token(self, token: str) -> None:
        """
        Revoke the given token.

        :param token: The token to revoke.
        """
        pass


class JWTManageService(TokenManageService):
    """
    JWT-based implementation of the TokenManageService.
    """

    def __init__(
        self,
        storage: AsyncKeyValueStorage,
        secret: str,
        algorithm: str,
        access_token_expire_minutes: int,
        refresh_token_expire_days: int,
    ):
        """
        Initialize the JWTManageService.

        Args:
            storage (AsyncKeyValueStorage): The storage backend for tokens.
            secret (str): The secret key for encoding tokens.
            algorithm (str): The algorithm to use for encoding tokens.
            access_token_expire_minutes (int): The expiration time for access tokens in minutes.
            refresh_token_expire_days (int): The expiration time for refresh tokens in days.
        """
        if storage is None:
            raise ValueError('Storage cannot be None')
        self.storage = storage
        self._secret = secret
        self._algorithm = algorithm
        self._access_token_expire_minutes = access_token_expire_minutes
        self._refresh_token_expire_days = refresh_token_expire_days

    @property
    def secret(self) -> str:
        """
        Get the secret key.

        Returns:
            str: The secret key as a string.
        """
        return self._secret

    @secret.setter
    def secret(self, value: str):
        """
        Set the secret key.

        Args:
            value (str): The new secret key.
        """
        self._secret = value

    @property
    def algorithm(self) -> str:
        """
        Get the algorithm.

        Returns:
            str: The algorithm as a string.
        """
        return self._algorithm

    @algorithm.setter
    def algorithm(self, value: str):
        """
        Set the algorithm.

        Args:
            value (str): The new algorithm.
        """
        self._algorithm = value

    @property
    def access_token_expire_minutes(self) -> int:
        """
        Get the access token expiration time in minutes.

        Returns:
            int: The expiration time in minutes.
        """
        return self._access_token_expire_minutes

    @access_token_expire_minutes.setter
    def access_token_expire_minutes(self, value: int):
        """
        Set the access token expiration time in minutes.

        Args:
            value (int): The new expiration time in minutes.
        """
        if value <= 0:
            raise ValueError('access_token_expire_minutes must be greater than 0')
        self._access_token_expire_minutes = value

    @property
    def refresh_token_expire_days(self) -> int:
        """
        Get the refresh token expiration time in days.

        Returns:
            int: The expiration time in days.
        """
        return self._refresh_token_expire_days

    @refresh_token_expire_days.setter
    def refresh_token_expire_days(self, value: int):
        """
        Set the refresh token expiration time in days.

        Args:
            value (int): The new expiration time in days.
        """
        self._refresh_token_expire_days = value

    def encode_jwt(
        self,
        payload: dict,
        secret_key: Optional[str] = None,
        algorithm: Optional[str] = None,
        expire_minutes: Optional[int] = None,
        expire_timedelta: Optional[datetime.timedelta] = None,
    ) -> str:
        """
        Encode a JWT with the given payload and expiration time.

        Args:
            payload (dict): The payload to include in the JWT.
            secret_key (Optional[str]): The secret key to use for encoding.
            algorithm (Optional[str]): The algorithm to use for encoding.
            expire_minutes (Optional[int]): The expiration time in minutes.
            expire_timedelta (Optional[datetime.timedelta]): The expiration time as a timedelta.

        Returns:
            str: The encoded JWT as a string.
        """
        try:
            secret_key = secret_key or self.secret
            algorithm = algorithm or self.algorithm
            expire_minutes = expire_minutes or self._access_token_expire_minutes

            to_encode = payload.copy()
            now = datetime.datetime.now(datetime.UTC)
            expire = now + (
                expire_timedelta
                if expire_timedelta
                else datetime.timedelta(minutes=expire_minutes)
            )
            to_encode.update({'exp': expire, 'iat': now})
            logger.debug(f"Encoding JWT with payload: {to_encode}")
            return jwt.encode(to_encode, secret_key, algorithm=algorithm)
        except Exception as e:
            logger.error(f"Failed to encode JWT: {e}")
            raise

    def create_token(
        self,
        token_type: TokenType,
        token_data: dict,
        expire_minutes: Optional[int] = None,
        expire_timedelta: Optional[datetime.timedelta] = None,
    ) -> str:
        """
        Create a token with the given data, expiration time, and token type.

        Args:
            token_type (TokenType): The type of the token.
            token_data (dict): The data to include in the token payload.
            expire_minutes (Optional[int]): The expiration time in minutes.
            expire_timedelta (Optional[datetime.timedelta]): The expiration time as a timedelta.

        Returns:
            str: The encoded token as a string.
        """
        try:
            expire_minutes = expire_minutes or self._access_token_expire_minutes
            jwt_payload = {TOKEN_TYPE_FIELD: token_type.value}
            jwt_payload.update(token_data)
            logger.debug(
                f"Creating token of type {token_type} with data: {jwt_payload}",
            )
            return self.encode_jwt(
                payload=jwt_payload,
                expire_minutes=expire_minutes,
                expire_timedelta=expire_timedelta,
            )
        except Exception as e:
            logger.error(f"Failed to create token: {e}")
            raise

    async def create_access_token(self, user: User) -> str:
        """
        Create an access token for the given user.

        Args:
            user (UserInDB): The user for whom to create the access token.

        Returns:
            str: The created access token.
        """
        try:
            jwt_payload = {
                'sub': str(user.id),
                'jti': str(uuid.uuid4()),
            }
            access_token = self.create_token(
                token_type=TokenType.ACCESS,
                token_data=jwt_payload,
            )
            await self.storage.add_user_token(
                str(user.id),
                access_token,
                TokenType.ACCESS,
                self._access_token_expire_minutes * 60,
            )
            return access_token
        except Exception as e:
            logger.error(f"Failed to create access token: {e}")
            raise

    async def create_refresh_token(self, user: User) -> str:
        """
        Create a refresh token for the given user.

        Args:
            user (UserInDB): The user for whom to create the refresh token.

        Returns:
            str: The created refresh token.
        """
        try:
            jwt_payload = {'sub': str(user.id)}
            try:
                refresh_token = self.create_token(
                    token_type=TokenType.REFRESH,
                    token_data=jwt_payload,
                    expire_timedelta=datetime.timedelta(
                        days=self._refresh_token_expire_days,
                    ),
                )
            except Exception as e:
                logger.error(f"Failed to create refresh token: {e}")
                raise

            try:
                await self.storage.add_user_token(
                    str(user.id),
                    refresh_token,
                    TokenType.REFRESH,
                    self._refresh_token_expire_days * 24 * 60 * 60,
                )
            except Exception as e:
                logger.error(f"Failed to store refresh token: {e}")
                raise

            return refresh_token
        except Exception as e:
            logger.error(f"Failed to create refresh token for user {user.id}: {e}")
            raise

    async def create_token_pair(self, user: User) -> TokenInfo:
        """
        Create a pair of access and refresh tokens for the given user.

        Args:
            user (UserInDB): The user for whom to create the token pair.

        Returns:
            TokenInfo: The created token pair.
        """
        try:
            access_token = await self.create_access_token(user)
            refresh_token = await self.create_refresh_token(user)
            return TokenInfo(access_token=access_token, refresh_token=refresh_token)
        except Exception as e:
            logger.error(f"Failed to create token pair: {e}")
            raise

    @staticmethod
    def decode_jwt(token: str, secret_key: str, algorithm: str) -> dict[str, Any]:
        """
        Decode a JWT.

        Args:
            token (str): The JWT to decode.
            secret_key (str): The secret key to use for decoding.
            algorithm (str): The algorithm to use for decoding.

        Returns:
            Dict[str, Any]: The decoded token payload.
        """
        try:
            logger.debug(f"Decoding JWT: {token}")
            return jwt.decode(token, secret_key, algorithms=[algorithm])
        except Exception as e:
            logger.error(f"Failed to decode JWT: {e}")
            raise

    async def revoke_token(self, token: str) -> None:
        """
        Revoke the given token.

        Args:
            token (str): The token to revoke.
        """
        try:
            await self.storage.blacklist_token(
                token, self._access_token_expire_minutes * 60,
            )
        except Exception as e:
            logger.error(f"Failed to revoke token: {e}")
            raise

    async def revoke_all_tokens_for_user(self, user_id: str) -> None:
        """
        Revoke all tokens for the given user.

        Args:
            user_id (str): The ID of the user.
        """
        try:
            access_tokens = await self.storage.get_user_tokens(
                user_id, TokenType.ACCESS,
            )
            refresh_tokens = await self.storage.get_user_tokens(
                user_id, TokenType.REFRESH,
            )

            for token in access_tokens:
                await self.revoke_token(token.decode('utf-8'))

            for token in refresh_tokens:
                await self.revoke_token(token.decode('utf-8'))

            await self.storage.delete(f"user:{user_id}:access_tokens")
            await self.storage.delete(f"user:{user_id}:refresh_tokens")
        except Exception as e:
            logger.error(f"Failed to revoke all tokens for user {user_id}: {e}")
            raise

    async def validate_token(self, token: str, token_type: TokenType) -> dict:
        """
        Validate the given token and return its payload.

        Args:
            token (str): The token to validate.
            token_type (TokenType): The type of the token.

        Returns:
            dict: The decoded token payload.
        """
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            if payload.get(TOKEN_TYPE_FIELD) != token_type:
                raise jwt.InvalidTokenError('Invalid token type')
            if await self.storage.is_token_blacklisted(token):
                raise jwt.InvalidTokenError('Token has been revoked')
            return payload
        except jwt.ExpiredSignatureError:
            logger.error('Token has expired')
            raise jwt.InvalidTokenError('Token has expired')
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {e}")
            raise e
        except Exception as e:
            logger.error(f"Failed to validate token: {e}")
            raise
