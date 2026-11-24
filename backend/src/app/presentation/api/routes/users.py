from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.application.cqrs.users import (
    AssignRoleToUserCommand,
    AssignRoleToUserHandler,
    GetUserHandler,
    GetUserQuery,
    ListUsersHandler,
    ListUsersQuery,
)
from app.domain.entities import User
from app.domain.permissions import PermissionCode
from app.presentation.api.dependencies import UnitOfWorkDep, permission_policy
from app.presentation.schemas.auth import AssignRoleRequest, UserResponse

router = APIRouter(prefix="/users")
UserReader = Annotated[User, Depends(permission_policy(PermissionCode.USERS_READ.value))]
UserManager = Annotated[User, Depends(permission_policy(PermissionCode.USERS_MANAGE.value))]


@router.get("", response_model=list[UserResponse])
async def list_users(
    _: UserReader,
    unit_of_work: UnitOfWorkDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[UserResponse]:
    users = await ListUsersHandler(unit_of_work.users).handle(
        ListUsersQuery(offset=offset, limit=limit)
    )
    return [UserResponse.model_validate(user) for user in users]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID, _: UserReader, unit_of_work: UnitOfWorkDep) -> UserResponse:
    user = await GetUserHandler(unit_of_work.users).handle(GetUserQuery(user_id))
    return UserResponse.model_validate(user)


@router.post("/{user_id}/roles", response_model=UserResponse)
async def assign_role(
    user_id: UUID,
    payload: AssignRoleRequest,
    _: UserManager,
    unit_of_work: UnitOfWorkDep,
) -> UserResponse:
    user = await AssignRoleToUserHandler(
        unit_of_work.users,
        unit_of_work.roles,
    ).handle(AssignRoleToUserCommand(user_id=user_id, role_id=payload.role_id))
    return UserResponse.model_validate(user)
