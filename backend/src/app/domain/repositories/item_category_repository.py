from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from app.domain.entities import ItemCategory


class ItemCategoryRepository(Protocol):
    async def add(self, category: ItemCategory) -> ItemCategory: ...
    async def get(self, category_id: UUID) -> ItemCategory | None: ...
    async def list_by_catalog(self, catalog_id: UUID) -> Sequence[ItemCategory]: ...
