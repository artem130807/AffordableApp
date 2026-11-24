from dataclasses import dataclass
from uuid import UUID

from app.domain.entities import Catalog
from app.domain.repositories import CatalogRepository


@dataclass(frozen=True, slots=True)
class ListCatalogsQuery:
    organization_id: UUID


class ListCatalogsHandler:
    def __init__(self, catalogs: CatalogRepository) -> None:
        self.catalogs = catalogs

    async def handle(self, query: ListCatalogsQuery) -> list[Catalog]:
        return list(await self.catalogs.list_by_organization(query.organization_id))
