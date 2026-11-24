from collections.abc import Sequence
from dataclasses import asdict
from decimal import Decimal
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import CatalogItem, Organization, PriceUnit
from app.infrastructure.orm.models import CatalogItemModel, CatalogModel, OrganizationModel
from app.infrastructure.repositories.organization_repository import organization_to_domain


def catalog_item_to_domain(model: CatalogItemModel) -> CatalogItem:
    return CatalogItem(
        id=model.id,
        catalog_id=model.catalog_id,
        category_id=model.category_id,
        name=model.name,
        description=model.description,
        price=model.price,
        currency=model.currency,
        price_unit=PriceUnit(model.price_unit),
        attributes=model.attributes,
        is_available=model.is_available,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SqlAlchemyCatalogItemRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, item: CatalogItem) -> CatalogItem:
        values = asdict(item)
        values["price_unit"] = item.price_unit.value
        model = CatalogItemModel(**values)
        self.session.add(model)
        await self.session.flush()
        return catalog_item_to_domain(model)

    async def get(self, item_id: UUID) -> CatalogItem | None:
        model = await self.session.get(CatalogItemModel, item_id)
        return catalog_item_to_domain(model) if model else None

    async def list_by_catalog(
        self,
        catalog_id: UUID,
        *,
        available_only: bool = True,
    ) -> Sequence[CatalogItem]:
        query = select(CatalogItemModel).where(CatalogItemModel.catalog_id == catalog_id)
        if available_only:
            query = query.where(CatalogItemModel.is_available.is_(True))
        result = await self.session.scalars(query.order_by(CatalogItemModel.price))
        return [catalog_item_to_domain(model) for model in result]

    async def list_affordable(
        self,
        budget: Decimal | None,
        *,
        currency: str,
        organization_type_id: UUID | None = None,
        city: str | None = None,
        wishes: str | None = None,
    ) -> Sequence[tuple[Organization, CatalogItem]]:
        query = (
            select(OrganizationModel, CatalogItemModel)
            .join(CatalogModel, CatalogModel.organization_id == OrganizationModel.id)
            .join(CatalogItemModel, CatalogItemModel.catalog_id == CatalogModel.id)
            .where(
                OrganizationModel.is_active.is_(True),
                CatalogModel.is_active.is_(True),
                CatalogItemModel.is_available.is_(True),
                CatalogItemModel.currency == currency,
            )
        )
        if budget is not None:
            query = query.where(CatalogItemModel.price <= budget)
        if organization_type_id:
            query = query.where(OrganizationModel.type_id == organization_type_id)
        if city:
            query = query.where(OrganizationModel.city.ilike(city))
        if wishes:
            pattern = f"%{wishes}%"
            query = query.where(
                or_(
                    OrganizationModel.name.ilike(pattern),
                    OrganizationModel.description.ilike(pattern),
                    CatalogItemModel.name.ilike(pattern),
                    CatalogItemModel.description.ilike(pattern),
                )
            )
        rows = (await self.session.execute(query.order_by(CatalogItemModel.price))).all()
        return [
            (organization_to_domain(organization), catalog_item_to_domain(item))
            for organization, item in rows
        ]
