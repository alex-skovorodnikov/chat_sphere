import logging
from fastapi import APIRouter, Depends, HTTPException
from src.schemas.entity import Group, GroupCreate
from typing import Annotated
from src.depends.dependencies import get_group_service, get_current_user
from src.services.groups import CustomGroupService


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    '',
    response_model=list[Group],
)
async def get_groups(
    group_service: Annotated[CustomGroupService, Depends(get_group_service)],
):
    return await group_service.get()


@router.post(
    '/{group_id}/add_user',
    # response_model=str,
    summary='Add user to group',
    description='Add a user to a specific group',
    responses={200: {'description': 'User added to group successfully'}},
)
async def add_user_to_group(
    group_id: str,
    user_id: Annotated[str, Depends(get_current_user)],
    group_service: Annotated[CustomGroupService, Depends(get_group_service)],
):
    try:
        await group_service.add_user_to_group(group_id, user_id)
        return {'message': 'User added to group successfully'}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    '',
    response_model=Group,
    summary='Create a new group',
    description='Create a new group in the system',
    responses={200: {'description': 'The created group'}},
)
async def create_group(
    new_group: GroupCreate,
    group_service: Annotated[CustomGroupService, Depends(get_group_service)],
):
    group = await group_service.create(new_group)
    return group
