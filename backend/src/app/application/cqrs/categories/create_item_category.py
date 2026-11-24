from dataclasses import dataclass
from uuid import UUID

from app.application.services.authorization import OrganizationOwnershipPolicy
from app.domain.entities import ItemCategory, User
from app.domain.repositories import (
    CatalogRepository,
    ItemCategoryRepository,
    OrganizationRepository,
)
from app.domain.validation import normalize_required_text


@dataclass(frozen=True, slots=True)
class CreateItemCategoryCommand:
    catalog_id: UUID
    actor: User
    name: str
    description: str | None = None


class CreateItemCategoryHandler:
    def __init__(
        self,
        categories: ItemCategoryRepository,
        catalogs: CatalogRepository,
        organizations: OrganizationRepository,
    ) -> None:
        self.categories = categories
        self.ownership = OrganizationOwnershipPolicy(organizations, catalogs)

    async def handle(self, command: CreateItemCategoryCommand) -> ItemCategory:
        await self.ownership.ensure_catalog_owner(command.catalog_id, command.actor)
        name = normalize_required_text(
            command.name,
            field_name="Название категории",
            min_length=1,
            max_length=120,
        )
        return await self.categories.add(
            ItemCategory(
                catalog_id=command.catalog_id,
                name=name,
                description=command.description,
            )
        )
