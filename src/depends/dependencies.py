import logging
import jwt
import redis.asyncio as redis

from functools import lru_cache
from jwt import InvalidTokenError

from fastapi import Depends, HTTPException, status, Form, WebSocket, Query, WebSocketException
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from redis.asyncio import Redis

from src.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.users_service import CustomUserService
from src.db.postgres import get_session
from src.db.token_storage import RedisStorage
from src.schemas.entity import User
from src.schemas.token import TokenType
from src.services.token_service import JWTManageService
from src.managers.websocket_manager import WebSocketConnectionManager
from src.services.history_service import CustomHistoryService


logger = logging.getLogger(__name__)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/v1/auth/signin')


def get_pagination_params(
    limit: int = Query(10, le=100),
    offset: int = Query(0),
):
    return limit, offset


async def get_token(
    websocket: WebSocket,
    # session: Annotated[str | None, Cookie()] = None,
    token: Annotated[str | None, Query()] = None,
):
    if token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    return token


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, settings.security.secret_key, algorithms=[settings.security.algorithm])
        user_id = payload.get('sub')
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    return user_id


@lru_cache
def get_user_service(
    db: AsyncSession = Depends(get_session),
) -> CustomUserService:
    return CustomUserService(db=db)


@lru_cache
def get_history_service(db: AsyncSession = Depends(get_session)) -> CustomHistoryService:
    return CustomHistoryService(db=db)


async def validate_user(
    user_service: Annotated[CustomUserService, Depends(get_user_service)],
    username: str = Form(),
    password: str = Form(),
) -> User:
    user = await user_service.get_user(user_name=username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    if not user_service.verify_password(
            hashed_password=user.password,
            provided_password=password,
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    return user


def get_redis() -> Redis:
    pool = redis.ConnectionPool(
        host=settings.redis.host,
        port=settings.redis.port,
        decode_responses=True,
    )
    return redis.Redis(connection_pool=pool)


@lru_cache
def get_redis_storage(redis_client: Redis = Depends(get_redis)) -> RedisStorage:
    return RedisStorage(redis_client)


@lru_cache
def get_token_service(
    token_storage: Annotated[RedisStorage, Depends(get_redis_storage)],
) -> JWTManageService:
    return JWTManageService(
        storage=token_storage,
        secret=settings.security.secret_key,
        algorithm=settings.security.algorithm,
        access_token_expire_minutes=settings.security.access_token_expire_minutes,
        refresh_token_expire_days=settings.security.refresh_token_expire_days,
    )


async def get_current_token_payload(
    token: str = Depends(oauth2_scheme),
    token_service: JWTManageService = Depends(get_token_service),
) -> dict:
    try:
        payload = token_service.decode_jwt(
            token=token,
            secret_key=token_service.secret,
            algorithm=token_service.algorithm,
        )
        await token_service.validate_token(
            token=token,
            token_type=payload.get('type'),
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"invalid token error: {e}",
        )
    return payload


@lru_cache
def get_websocket_manager() -> WebSocketConnectionManager:
    return WebSocketConnectionManager()


class UserGetterFromToken:
    def __init__(
        self,
        token_type: TokenType,
    ):
        self.token_type = token_type

    def __validate_token_type(self, payload: dict):
        if (current_token_type := payload.get('type')) != self.token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type {current_token_type!r} expected {self.token_type!r}",
            )

    @staticmethod
    async def get_user_by_token_sub(payload: dict, user_service: CustomUserService):
        return await user_service.get_user(user_id=payload['sub'])

    async def __call__(
        self,
        payload: dict = Depends(get_current_token_payload),
        user_service: CustomUserService = Depends(get_user_service),
    ):
        self.__validate_token_type(payload)
        return await self.get_user_by_token_sub(payload, user_service)


get_current_auth_user = UserGetterFromToken(
    TokenType.ACCESS,
)

get_current_auth_user_for_refresh = UserGetterFromToken(
    TokenType.REFRESH,
)
