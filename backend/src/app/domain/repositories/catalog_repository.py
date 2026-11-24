from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from app.domain.entities import Catalog


class CatalogRepository(Protocol):
    async def add(self, catalog: Catalog) -> Catalog: ...
    async def get(self, catalog_id: UUID) -> Catalog | None: ...
    async def list_by_organization(self, organization_id: UUID) -> Sequence[Catalog]: ...
