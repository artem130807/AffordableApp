from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from app.domain.entities import RecommendationFilter


class RecommendationFilterRepository(Protocol):
    async def add(self, recommendation_filter: RecommendationFilter) -> RecommendationFilter: ...

    async def get(self, filter_id: UUID) -> RecommendationFilter | None: ...

    async def list_by_user(
        self,
        user_id: UUID,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[RecommendationFilter]: ...
