from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.application.cqrs.roles import (
    AssignPermissionToRoleCommand,
    AssignPermissionToRoleHandler,
    CreateRoleCommand,
    CreateRoleHandler,
    ListRolesHandler,
)
from app.domain.entities import User
from app.domain.permissions import PermissionCode
from app.presentation.api.dependencies import UnitOfWorkDep, permission_policy
from app.presentation.schemas.auth import AssignPermissionRequest, RoleCreateRequest, RoleResponse

router = APIRouter(prefix="/roles")
RoleManager = Annotated[User, Depends(permission_policy(PermissionCode.ROLES_MANAGE.value))]


@router.get("", response_model=list[RoleResponse])
async def list_roles(_: RoleManager, unit_of_work: UnitOfWorkDep) -> list[RoleResponse]:
    roles = await ListRolesHandler(unit_of_work.roles).handle()
    return [RoleResponse.model_validate(role) for role in roles]


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    payload: RoleCreateRequest,
    _: RoleManager,
    unit_of_work: UnitOfWorkDep,
) -> RoleResponse:
    role = await CreateRoleHandler(
        unit_of_work.roles,
        unit_of_work.permissions,
    ).handle(CreateRoleCommand(**payload.model_dump()))
    return RoleResponse.model_validate(role)


@router.post("/{role_id}/permissions", response_model=RoleResponse)
async def assign_permission(
    role_id: UUID,
    payload: AssignPermissionRequest,
    _: RoleManager,
    unit_of_work: UnitOfWorkDep,
) -> RoleResponse:
    role = await AssignPermissionToRoleHandler(
        unit_of_work.roles,
        unit_of_work.permissions,
    ).handle(AssignPermissionToRoleCommand(role_id=role_id, permission_id=payload.permission_id))
    return RoleResponse.model_validate(role)
