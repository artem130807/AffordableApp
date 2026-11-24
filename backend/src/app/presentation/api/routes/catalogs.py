from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.application.cqrs.catalogs import (
    CreateCatalogCommand,
    CreateCatalogHandler,
    GetCatalogHandler,
    GetCatalogQuery,
    ListCatalogsHandler,
    ListCatalogsQuery,
)
from app.application.cqrs.categories import (
    CreateItemCategoryCommand,
    CreateItemCategoryHandler,
    GetItemCategoryHandler,
    GetItemCategoryQuery,
    ListItemCategoriesHandler,
    ListItemCategoriesQuery,
)
from app.application.cqrs.items import (
    CreateCatalogItemCommand,
    CreateCatalogItemHandler,
    GetCatalogItemHandler,
    GetCatalogItemQuery,
    ListCatalogItemsHandler,
    ListCatalogItemsQuery,
)
from app.domain.entities import User
from app.domain.permissions import PermissionCode
from app.presentation.api.dependencies import UnitOfWorkDep, permission_policy
from app.presentation.schemas.organizations import (
    CatalogCreateRequest,
    CatalogItemCreateRequest,
    CatalogItemResponse,
    CatalogResponse,
    CategoryCreateRequest,
    CategoryResponse,
)

router = APIRouter()
CatalogManager = Annotated[
    User,
    Depends(permission_policy(PermissionCode.CATALOGS_MANAGE.value)),
]
ItemManager = Annotated[User, Depends(permission_policy(PermissionCode.ITEMS_MANAGE.value))]


@router.get("/catalogs/{catalog_id}", response_model=CatalogResponse)
async def get_catalog(catalog_id: UUID, unit_of_work: UnitOfWorkDep) -> CatalogResponse:
    result = await GetCatalogHandler(unit_of_work.catalogs).handle(GetCatalogQuery(catalog_id))
    return CatalogResponse.model_validate(result)


@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: UUID, unit_of_work: UnitOfWorkDep) -> CategoryResponse:
    result = await GetItemCategoryHandler(unit_of_work.categories).handle(
        GetItemCategoryQuery(category_id)
    )
    return CategoryResponse.model_validate(result)


@router.get("/items/{item_id}", response_model=CatalogItemResponse)
async def get_item(item_id: UUID, unit_of_work: UnitOfWorkDep) -> CatalogItemResponse:
    result = await GetCatalogItemHandler(unit_of_work.items).handle(GetCatalogItemQuery(item_id))
    return CatalogItemResponse.model_validate(result)


@router.get("/organizations/{organization_id}/catalogs", response_model=list[CatalogResponse])
async def list_catalogs(
    organization_id: UUID,
    unit_of_work: UnitOfWorkDep,
) -> list[CatalogResponse]:
    results = await ListCatalogsHandler(unit_of_work.catalogs).handle(
        ListCatalogsQuery(organization_id=organization_id)
    )
    return [CatalogResponse.model_validate(item) for item in results]


@router.post(
    "/organizations/{organization_id}/catalogs",
    response_model=CatalogResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_catalog(
    organization_id: UUID,
    payload: CatalogCreateRequest,
    user: CatalogManager,
    unit_of_work: UnitOfWorkDep,
) -> CatalogResponse:
    result = await CreateCatalogHandler(
        unit_of_work.catalogs,
        unit_of_work.organizations,
    ).handle(
        CreateCatalogCommand(
            organization_id=organization_id,
            actor=user,
            **payload.model_dump(),
        )
    )
    return CatalogResponse.model_validate(result)


@router.get("/catalogs/{catalog_id}/categories", response_model=list[CategoryResponse])
async def list_categories(catalog_id: UUID, unit_of_work: UnitOfWorkDep) -> list[CategoryResponse]:
    results = await ListItemCategoriesHandler(unit_of_work.categories).handle(
        ListItemCategoriesQuery(catalog_id=catalog_id)
    )
    return [CategoryResponse.model_validate(item) for item in results]


@router.post(
    "/catalogs/{catalog_id}/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    catalog_id: UUID,
    payload: CategoryCreateRequest,
    user: ItemManager,
    unit_of_work: UnitOfWorkDep,
) -> CategoryResponse:
    result = await CreateItemCategoryHandler(
        unit_of_work.categories,
        unit_of_work.catalogs,
        unit_of_work.organizations,
    ).handle(
        CreateItemCategoryCommand(
            catalog_id=catalog_id,
            actor=user,
            **payload.model_dump(),
        )
    )
    return CategoryResponse.model_validate(result)


@router.get("/catalogs/{catalog_id}/items", response_model=list[CatalogItemResponse])
async def list_items(catalog_id: UUID, unit_of_work: UnitOfWorkDep) -> list[CatalogItemResponse]:
    results = await ListCatalogItemsHandler(unit_of_work.items).handle(
        ListCatalogItemsQuery(catalog_id=catalog_id)
    )
    return [CatalogItemResponse.model_validate(item) for item in results]


@router.post(
    "/catalogs/{catalog_id}/items",
    response_model=CatalogItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_item(
    catalog_id: UUID,
    payload: CatalogItemCreateRequest,
    user: ItemManager,
    unit_of_work: UnitOfWorkDep,
) -> CatalogItemResponse:
    result = await CreateCatalogItemHandler(
        unit_of_work.items,
        unit_of_work.catalogs,
        unit_of_work.categories,
        unit_of_work.organizations,
    ).handle(
        CreateCatalogItemCommand(
            catalog_id=catalog_id,
            actor=user,
            **payload.model_dump(),
        )
    )
    return CatalogItemResponse.model_validate(result)
