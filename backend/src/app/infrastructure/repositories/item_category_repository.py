from collections.abc import Sequence
from dataclasses import asdict
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import ItemCategory
from app.infrastructure.orm.models import ItemCategoryModel


def item_category_to_domain(model: ItemCategoryModel) -> ItemCategory:
    return ItemCategory(
        id=model.id,
        catalog_id=model.catalog_id,
        name=model.name,
        description=model.description,
    )


class SqlAlchemyItemCategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, category: ItemCategory) -> ItemCategory:
        model = ItemCategoryModel(**asdict(category))
        self.session.add(model)
        await self.session.flush()
        return item_category_to_domain(model)

    async def get(self, category_id: UUID) -> ItemCategory | None:
        model = await self.session.get(ItemCategoryModel, category_id)
        return item_category_to_domain(model) if model else None

    async def list_by_catalog(self, catalog_id: UUID) -> Sequence[ItemCategory]:
        result = await self.session.scalars(
            select(ItemCategoryModel)
            .where(ItemCategoryModel.catalog_id == catalog_id)
            .order_by(ItemCategoryModel.name)
        )
        return [item_category_to_domain(model) for model in result]
