from collections.abc import Sequence
from dataclasses import asdict
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import RecommendationFilter
from app.infrastructure.orm.models import RecommendationFilterModel


def recommendation_filter_to_domain(model: RecommendationFilterModel) -> RecommendationFilter:
    return RecommendationFilter(
        id=model.id,
        user_id=model.user_id,
        client_id=model.client_id,
        organization_type_id=model.organization_type_id,
        budget=model.budget,
        party_size=model.party_size,
        city=model.city,
        wishes=model.wishes,
        currency=model.currency,
        created_at=model.created_at,
    )


class SqlAlchemyRecommendationFilterRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, recommendation_filter: RecommendationFilter) -> RecommendationFilter:
        model = RecommendationFilterModel(**asdict(recommendation_filter))
        self.session.add(model)
        await self.session.flush()
        return recommendation_filter_to_domain(model)

    async def get(self, filter_id: UUID) -> RecommendationFilter | None:
        model = await self.session.get(RecommendationFilterModel, filter_id)
        return recommendation_filter_to_domain(model) if model else None

    async def list_by_user(
        self,
        user_id: UUID,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[RecommendationFilter]:
        result = await self.session.scalars(
            select(RecommendationFilterModel)
            .where(RecommendationFilterModel.user_id == user_id)
            .order_by(RecommendationFilterModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return [recommendation_filter_to_domain(model) for model in result]
