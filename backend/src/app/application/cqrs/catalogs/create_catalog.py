from dataclasses import dataclass
from uuid import UUID

from app.application.services.authorization import OrganizationOwnershipPolicy
from app.domain.entities import Catalog, User
from app.domain.repositories import CatalogRepository, OrganizationRepository
from app.domain.validation import normalize_required_text


@dataclass(frozen=True, slots=True)
class CreateCatalogCommand:
    organization_id: UUID
    actor: User
    name: str
    description: str | None = None


class CreateCatalogHandler:
    def __init__(
        self,
        catalogs: CatalogRepository,
        organizations: OrganizationRepository,
    ) -> None:
        self.catalogs = catalogs
        self.ownership = OrganizationOwnershipPolicy(organizations, catalogs)

    async def handle(self, command: CreateCatalogCommand) -> Catalog:
        await self.ownership.ensure_organization_owner(command.organization_id, command.actor)
        name = normalize_required_text(
            command.name,
            field_name="Название каталога",
            min_length=1,
            max_length=180,
        )
        return await self.catalogs.add(
            Catalog(
                organization_id=command.organization_id,
                name=name,
                description=command.description,
            )
        )
