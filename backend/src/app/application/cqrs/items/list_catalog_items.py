from dataclasses import dataclass
from uuid import UUID

from app.domain.entities import CatalogItem
from app.domain.repositories import CatalogItemRepository


@dataclass(frozen=True, slots=True)
class ListCatalogItemsQuery:
    catalog_id: UUID
    available_only: bool = True


class ListCatalogItemsHandler:
    def __init__(self, items: CatalogItemRepository) -> None:
        self.items = items

    async def handle(self, query: ListCatalogItemsQuery) -> list[CatalogItem]:
        return list(
            await self.items.list_by_catalog(
                query.catalog_id,
                available_only=query.available_only,
            )
        )
