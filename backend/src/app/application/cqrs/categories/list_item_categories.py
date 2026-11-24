from dataclasses import dataclass
from uuid import UUID

from app.domain.entities import ItemCategory
from app.domain.repositories import ItemCategoryRepository


@dataclass(frozen=True, slots=True)
class ListItemCategoriesQuery:
    catalog_id: UUID


class ListItemCategoriesHandler:
    def __init__(self, categories: ItemCategoryRepository) -> None:
        self.categories = categories

    async def handle(self, query: ListItemCategoriesQuery) -> list[ItemCategory]:
        return list(await self.categories.list_by_catalog(query.catalog_id))
