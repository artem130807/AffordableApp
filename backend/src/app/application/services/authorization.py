from uuid import UUID

from app.domain.entities import User
from app.domain.exceptions import NotFoundError, PermissionDeniedError
from app.domain.permissions import PermissionCode
from app.domain.repositories import CatalogRepository, OrganizationRepository


class OrganizationOwnershipPolicy:
    def __init__(
        self,
        organizations: OrganizationRepository,
        catalogs: CatalogRepository,
    ) -> None:
        self.organizations = organizations
        self.catalogs = catalogs

    async def ensure_organization_owner(self, organization_id: UUID, user: User) -> None:
        organization = await self.organizations.get(organization_id)
        if organization is None:
            raise NotFoundError("Организация не найдена")
        if not organization.is_active:
            raise PermissionDeniedError("Организация неактивна")
        is_platform_admin = user.has_permission(PermissionCode.ORGANIZATIONS_ADMIN.value)
        if organization.owner_id != user.id and not is_platform_admin:
            raise PermissionDeniedError("Изменять каталог может только владелец организации")

    async def ensure_catalog_owner(self, catalog_id: UUID, user: User) -> None:
        catalog = await self.catalogs.get(catalog_id)
        if catalog is None:
            raise NotFoundError("Каталог не найден")
        if not catalog.is_active:
            raise PermissionDeniedError("Каталог неактивен")
        await self.ensure_organization_owner(catalog.organization_id, user)
