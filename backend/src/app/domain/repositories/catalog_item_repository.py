from collections.abc import Sequence
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from app.domain.entities import CatalogItem, Organization


class CatalogItemRepository(Protocol):
    async def add(self, item: CatalogItem) -> CatalogItem: ...
    async def get(self, item_id: UUID) -> CatalogItem | None: ...
    async def list_by_catalog(
        self,
        catalog_id: UUID,
        *,
        available_only: bool = True,
    ) -> Sequence[CatalogItem]: ...
    async def list_affordable(
        self,
        budget: Decimal | None,
        *,
        currency: str,
        organization_type_id: UUID | None = None,
        city: str | None = None,
        wishes: str | None = None,
    ) -> Sequence[tuple[Organization, CatalogItem]]: ...
