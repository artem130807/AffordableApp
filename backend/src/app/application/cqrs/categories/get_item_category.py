from dataclasses import dataclass
from uuid import UUID

from app.domain.entities import ItemCategory
from app.domain.exceptions import NotFoundError
from app.domain.repositories import ItemCategoryRepository


@dataclass(frozen=True, slots=True)
class GetItemCategoryQuery:
    category_id: UUID


class GetItemCategoryHandler:
    def __init__(self, categories: ItemCategoryRepository) -> None:
        self.categories = categories

    async def handle(self, query: GetItemCategoryQuery) -> ItemCategory:
        category = await self.categories.get(query.category_id)
        if category is None:
            raise NotFoundError("Категория не найдена")
        return category
