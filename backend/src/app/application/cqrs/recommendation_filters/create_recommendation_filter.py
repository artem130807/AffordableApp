from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from app.domain.entities import RecommendationFilter
from app.domain.exceptions import NotFoundError, ValidationError
from app.domain.repositories import OrganizationTypeRepository, RecommendationFilterRepository
from app.domain.validation import normalize_currency


@dataclass(frozen=True, slots=True)
class CreateRecommendationFilterCommand:
    client_id: UUID
    user_id: UUID | None = None
    organization_type_id: UUID | None = None
    budget: Decimal | None = None
    party_size: int | None = None
    city: str | None = None
    wishes: str | None = None
    currency: str = "RUB"


class CreateRecommendationFilterHandler:
    def __init__(
        self,
        filters: RecommendationFilterRepository,
        organization_types: OrganizationTypeRepository | None = None,
    ) -> None:
        self.filters = filters
        self.organization_types = organization_types

    async def handle(self, command: CreateRecommendationFilterCommand) -> RecommendationFilter:
        if command.budget is not None and command.budget < 0:
            raise ValidationError("Бюджет не может быть отрицательным")
        if command.party_size is not None and not 1 <= command.party_size <= 20:
            raise ValidationError("Количество участников должно быть от 1 до 20")
        if (
            command.organization_type_id is not None
            and self.organization_types is not None
            and await self.organization_types.get(command.organization_type_id) is None
        ):
            raise NotFoundError("Тип организации не найден")
        city = self._normalize_optional(command.city, field_name="Город", max_length=120)
        wishes = self._normalize_optional(
            command.wishes,
            field_name="Пожелания",
            max_length=500,
        )
        return await self.filters.add(
            RecommendationFilter(
                client_id=command.client_id,
                user_id=command.user_id,
                organization_type_id=command.organization_type_id,
                budget=command.budget,
                party_size=command.party_size,
                city=city,
                wishes=wishes,
                currency=normalize_currency(command.currency),
            )
        )

    @staticmethod
    def _normalize_optional(value: str | None, *, field_name: str, max_length: int) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if len(normalized) > max_length:
            raise ValidationError(f"{field_name} не может быть длиннее {max_length} символов")
        return normalized or None
