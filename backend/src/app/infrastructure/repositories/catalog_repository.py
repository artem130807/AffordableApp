from collections.abc import Sequence
from dataclasses import asdict
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Catalog
from app.infrastructure.orm.models import CatalogModel


def catalog_to_domain(model: CatalogModel) -> Catalog:
    return Catalog(
        id=model.id,
        organization_id=model.organization_id,
        name=model.name,
        description=model.description,
        is_active=model.is_active,
        created_at=model.created_at,
    )


class SqlAlchemyCatalogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, catalog: Catalog) -> Catalog:
        model = CatalogModel(**asdict(catalog))
        self.session.add(model)
        await self.session.flush()
        return catalog_to_domain(model)

    async def get(self, catalog_id: UUID) -> Catalog | None:
        model = await self.session.get(CatalogModel, catalog_id)
        return catalog_to_domain(model) if model else None

    async def list_by_organization(self, organization_id: UUID) -> Sequence[Catalog]:
        result = await self.session.scalars(
            select(CatalogModel)
            .where(
                CatalogModel.organization_id == organization_id,
                CatalogModel.is_active.is_(True),
            )
            .order_by(CatalogModel.name)
        )
        return [catalog_to_domain(model) for model in result]
