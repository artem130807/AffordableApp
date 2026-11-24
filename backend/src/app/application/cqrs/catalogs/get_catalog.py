from dataclasses import dataclass
from uuid import UUID

from app.domain.entities import Catalog
from app.domain.exceptions import NotFoundError
from app.domain.repositories import CatalogRepository


@dataclass(frozen=True, slots=True)
class GetCatalogQuery:
    catalog_id: UUID


class GetCatalogHandler:
    def __init__(self, catalogs: CatalogRepository) -> None:
        self.catalogs = catalogs

    async def handle(self, query: GetCatalogQuery) -> Catalog:
        catalog = await self.catalogs.get(query.catalog_id)
        if catalog is None:
            raise NotFoundError("Каталог не найден")
        return catalog
