from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any
from uuid import UUID

from app.application.services.authorization import OrganizationOwnershipPolicy
from app.domain.entities import CatalogItem, PriceUnit, User
from app.domain.exceptions import NotFoundError, ValidationError
from app.domain.repositories import (
    CatalogItemRepository,
    CatalogRepository,
    ItemCategoryRepository,
    OrganizationRepository,
)
from app.domain.validation import normalize_currency, normalize_required_text


@dataclass(frozen=True, slots=True)
class CreateCatalogItemCommand:
    catalog_id: UUID
    actor: User
    name: str
    price: Decimal
    category_id: UUID | None = None
    description: str | None = None
    currency: str = "RUB"
    price_unit: PriceUnit = PriceUnit.ITEM
    attributes: dict[str, Any] = field(default_factory=dict)


class CreateCatalogItemHandler:
    def __init__(
        self,
        items: CatalogItemRepository,
        catalogs: CatalogRepository,
        categories: ItemCategoryRepository,
        organizations: OrganizationRepository,
    ) -> None:
        self.items = items
        self.categories = categories
        self.ownership = OrganizationOwnershipPolicy(organizations, catalogs)

    async def handle(self, command: CreateCatalogItemCommand) -> CatalogItem:
        if command.price < 0:
            raise ValidationError("Цена не может быть отрицательной")
        await self.ownership.ensure_catalog_owner(command.catalog_id, command.actor)
        if command.category_id:
            category = await self.categories.get(command.category_id)
            if category is None or category.catalog_id != command.catalog_id:
                raise NotFoundError("Категория не найдена в этом каталоге")
        name = normalize_required_text(
            command.name,
            field_name="Название позиции",
            min_length=1,
            max_length=180,
        )
        currency = normalize_currency(command.currency)
        return await self.items.add(
            CatalogItem(
                catalog_id=command.catalog_id,
                category_id=command.category_id,
                name=name,
                description=command.description,
                price=command.price,
                currency=currency,
                price_unit=command.price_unit,
                attributes=command.attributes,
            )
        )
