from dataclasses import dataclass
from uuid import UUID

from app.domain.entities import RecommendationFilter
from app.domain.exceptions import ValidationError
from app.domain.repositories import RecommendationFilterRepository


@dataclass(frozen=True, slots=True)
class ListUserRecommendationFiltersQuery:
    user_id: UUID
    offset: int = 0
    limit: int = 100


class ListUserRecommendationFiltersHandler:
    def __init__(self, filters: RecommendationFilterRepository) -> None:
        self.filters = filters

    async def handle(
        self,
        query: ListUserRecommendationFiltersQuery,
    ) -> list[RecommendationFilter]:
        if query.offset < 0 or not 1 <= query.limit <= 100:
            raise ValidationError("Некорректные параметры пагинации")
        return list(
            await self.filters.list_by_user(
                query.user_id,
                offset=query.offset,
                limit=query.limit,
            )
        )
