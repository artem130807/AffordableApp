from typing import Protocol

from app.domain.repositories import (
    CatalogItemRepository,
    CatalogRepository,
    ItemCategoryRepository,
    OrganizationRepository,
    OrganizationTypeRepository,
    PermissionRepository,
    RecommendationFilterRepository,
    RefreshTokenRepository,
    RoleRepository,
    UserRepository,
)


class UnitOfWork(Protocol):
    """Application transaction boundary and repository registry."""

    @property
    def users(self) -> UserRepository: ...

    @property
    def roles(self) -> RoleRepository: ...

    @property
    def permissions(self) -> PermissionRepository: ...

    @property
    def organization_types(self) -> OrganizationTypeRepository: ...

    @property
    def organizations(self) -> OrganizationRepository: ...

    @property
    def catalogs(self) -> CatalogRepository: ...

    @property
    def categories(self) -> ItemCategoryRepository: ...

    @property
    def items(self) -> CatalogItemRepository: ...

    @property
    def refresh_tokens(self) -> RefreshTokenRepository: ...

    @property
    def recommendation_filters(self) -> RecommendationFilterRepository: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
