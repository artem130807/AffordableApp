from dataclasses import dataclass
from uuid import UUID

from app.domain.entities import CatalogItem
from app.domain.exceptions import NotFoundError
from app.domain.repositories import CatalogItemRepository


@dataclass(frozen=True, slots=True)
class GetCatalogItemQuery:
    item_id: UUID


class GetCatalogItemHandler:
    def __init__(self, items: CatalogItemRepository) -> None:
        self.items = items

    async def handle(self, query: GetCatalogItemQuery) -> CatalogItem:
        item = await self.items.get(query.item_id)
        if item is None:
            raise NotFoundError("Позиция каталога не найдена")
        return item
