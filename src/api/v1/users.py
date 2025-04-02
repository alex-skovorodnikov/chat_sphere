from fastapi import APIRouter, Depends
from src.depends.dependencies import get_user_service
from src.services.users import CustomUserService
from typing import Annotated
import logging
from src.schemas.entity import User, UserCreate

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    '',
    response_model=list[User],
    summary='Get all users',
    description='Get all users from the system',
    tags=['users'],
)
async def get_users(
    user_service: Annotated[CustomUserService, Depends(get_user_service)],
):
    users = await user_service.get_users()
    logger.info(f'Get users: {users}')  # Debugging purpose only
    return users


@router.post(
    '',
    response_model=User,
    summary='Create a new user',
    description='Create a new user in the system',
    tags=['users'],
)
async def create_user(
    new_user: UserCreate,
    user_service: Annotated[CustomUserService, Depends(get_user_service)],
):
    user = await user_service.create_user(new_user)
    return user


@router.get('/me')
async def get_user_info():
    return {'status': 'OK'}


@router.put('/me')
async def update_user(
        # user_id: Depends(get_current_user)
):
    return {'status': 'OK'}


# @router.post('/login')
# async def login_user():
#     return {'status': 'OK'}
#
# @router.post('/logout')
# async def logout_user():
#     return {'status': 'OK'}
#
# @router.post('/register')
# async def register_user():
#     return {'status': 'OK'}
