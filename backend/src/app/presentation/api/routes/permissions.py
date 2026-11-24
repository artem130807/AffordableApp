from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.application.cqrs.permissions import (
    CreatePermissionCommand,
    CreatePermissionHandler,
    ListPermissionsHandler,
)
from app.domain.entities import User
from app.domain.permissions import PermissionCode
from app.presentation.api.dependencies import UnitOfWorkDep, permission_policy
from app.presentation.schemas.auth import PermissionCreateRequest, PermissionResponse

router = APIRouter(prefix="/permissions")
PermissionManager = Annotated[
    User,
    Depends(permission_policy(PermissionCode.ROLES_MANAGE.value)),
]


@router.get("", response_model=list[PermissionResponse])
async def list_permissions(
    _: PermissionManager,
    unit_of_work: UnitOfWorkDep,
) -> list[PermissionResponse]:
    permissions = await ListPermissionsHandler(unit_of_work.permissions).handle()
    return [PermissionResponse.model_validate(permission) for permission in permissions]


@router.post("", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(
    payload: PermissionCreateRequest,
    _: PermissionManager,
    unit_of_work: UnitOfWorkDep,
) -> PermissionResponse:
    permission = await CreatePermissionHandler(unit_of_work.permissions).handle(
        CreatePermissionCommand(**payload.model_dump())
    )
    return PermissionResponse.model_validate(permission)
