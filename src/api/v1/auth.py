import logging

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from typing import Annotated
from src.services.users_service import CustomUserService
from src.services.token_service import JWTManageService
from src.depends.dependencies import (
    get_user_service,
    validate_user,
    get_token_service,
    get_current_auth_user_for_refresh,
)
from src.schemas.entity import UserCreate, User
from src.schemas.token import TokenInfo

logger = logging.getLogger(__name__)

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(dependencies=[Depends(http_bearer)])


@router.post(
    '/signup',
    response_model=User,
    summary='Create new user',
    description='Create a new user',
)
async def signup(
    user: UserCreate,
    user_service: Annotated[CustomUserService, Depends(get_user_service)],

):
    new_user = await user_service.create_user(user)
    logger.info('create_user')
    return new_user


@router.post(
    '/signin',
    response_model=TokenInfo,
    summary='Sign in user',
    description='Sign in user',
)
async def signin(
    user: Annotated[User, Depends(validate_user)],
    token_service: Annotated[JWTManageService, Depends(get_token_service)],
):
    token_data = await token_service.create_token_pair(user)
    return token_data


@router.post(
    '/refresh',
    response_model=TokenInfo,
    summary='Refresh token',
    description='Refresh token',
)
async def refresh(
    user: Annotated[User, Depends(get_current_auth_user_for_refresh)],
    token_service: Annotated[JWTManageService, Depends(get_token_service)],
):
    access_token = await token_service.create_access_token(user)
    refresh_token = await token_service.create_refresh_token(user)
    token_data = TokenInfo(access_token=access_token, refresh_token=refresh_token)
    return token_data
