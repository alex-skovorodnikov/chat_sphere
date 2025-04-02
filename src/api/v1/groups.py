from fastapi import APIRouter, Depends
from src.schemas.entity import Group, GroupCreate
from typing import Annotated
from src.depends.dependencies import get_group_service
from src.services.groups import CustomGroupService

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
