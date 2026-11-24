from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.application.cqrs.organization_types import (
    CreateOrganizationTypeCommand,
    CreateOrganizationTypeHandler,
    ListOrganizationTypesHandler,
)
from app.application.cqrs.organizations import (
    CreateOrganizationCommand,
    CreateOrganizationHandler,
    GetOrganizationHandler,
    GetOrganizationQuery,
    ListOrganizationsHandler,
    ListOrganizationsQuery,
)
from app.domain.entities import User
from app.domain.permissions import PermissionCode
from app.presentation.api.dependencies import UnitOfWorkDep, permission_policy
from app.presentation.schemas.organizations import (
    OrganizationCreateRequest,
    OrganizationResponse,
    OrganizationTypeCreateRequest,
    OrganizationTypeResponse,
)

router = APIRouter()
OrganizationManager = Annotated[
    User,
    Depends(permission_policy(PermissionCode.ORGANIZATIONS_MANAGE.value)),
]
RoleManager = Annotated[User, Depends(permission_policy(PermissionCode.ROLES_MANAGE.value))]


@router.get("/organization-types", response_model=list[OrganizationTypeResponse])
async def list_organization_types(unit_of_work: UnitOfWorkDep) -> list[OrganizationTypeResponse]:
    results = await ListOrganizationTypesHandler(unit_of_work.organization_types).handle()
    return [OrganizationTypeResponse.model_validate(item) for item in results]


@router.post(
    "/organization-types",
    response_model=OrganizationTypeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_organization_type(
    payload: OrganizationTypeCreateRequest,
    _: RoleManager,
    unit_of_work: UnitOfWorkDep,
) -> OrganizationTypeResponse:
    result = await CreateOrganizationTypeHandler(unit_of_work.organization_types).handle(
        CreateOrganizationTypeCommand(**payload.model_dump())
    )
    return OrganizationTypeResponse.model_validate(result)


@router.get("/organizations", response_model=list[OrganizationResponse])
async def list_organizations(
    unit_of_work: UnitOfWorkDep,
    type_id: UUID | None = None,
    city: str | None = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[OrganizationResponse]:
    results = await ListOrganizationsHandler(unit_of_work.organizations).handle(
        ListOrganizationsQuery(
            type_id=type_id,
            city=city,
            offset=offset,
            limit=limit,
        )
    )
    return [OrganizationResponse.model_validate(item) for item in results]


@router.get("/organizations/mine", response_model=list[OrganizationResponse])
async def list_my_organizations(
    user: OrganizationManager,
    unit_of_work: UnitOfWorkDep,
) -> list[OrganizationResponse]:
    results = await ListOrganizationsHandler(unit_of_work.organizations).handle(
        ListOrganizationsQuery(owner_id=user.id)
    )
    return [OrganizationResponse.model_validate(item) for item in results]


@router.get("/organizations/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: UUID,
    unit_of_work: UnitOfWorkDep,
) -> OrganizationResponse:
    result = await GetOrganizationHandler(unit_of_work.organizations).handle(
        GetOrganizationQuery(organization_id)
    )
    return OrganizationResponse.model_validate(result)


@router.post(
    "/organizations",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_organization(
    payload: OrganizationCreateRequest,
    user: OrganizationManager,
    unit_of_work: UnitOfWorkDep,
) -> OrganizationResponse:
    result = await CreateOrganizationHandler(
        unit_of_work.organizations,
        unit_of_work.organization_types,
    ).handle(CreateOrganizationCommand(owner_id=user.id, **payload.model_dump()))
    return OrganizationResponse.model_validate(result)
