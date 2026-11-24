from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from app.domain.entities import CatalogItem, Organization
from app.domain.exceptions import ValidationError
from app.domain.repositories import CatalogItemRepository
from app.domain.validation import normalize_currency


@dataclass(frozen=True, slots=True)
class FindAffordableOrganizationsQuery:
    budget: Decimal | None
    party_size: int | None = None
    currency: str = "RUB"
    organization_type_id: UUID | None = None
    city: str | None = None
    wishes: str | None = None
    limit: int = 20


@dataclass(frozen=True, slots=True)
class BudgetRecommendation:
    organization: Organization
    suggested_items: tuple[CatalogItem, ...]
    total: Decimal
    remaining_budget: Decimal | None


class FindAffordableOrganizationsHandler:
    def __init__(self, items: CatalogItemRepository) -> None:
        self.items = items

    async def handle(
        self,
        query: FindAffordableOrganizationsQuery,
    ) -> list[BudgetRecommendation]:
        if query.budget is not None and query.budget < 0:
            raise ValidationError("Бюджет не может быть отрицательным")
        if query.party_size is not None and not 1 <= query.party_size <= 20:
            raise ValidationError("Количество участников должно быть от 1 до 20")
        if not 1 <= query.limit <= 100:
            raise ValidationError("Лимит рекомендаций должен быть от 1 до 100")
        currency = normalize_currency(query.currency)
        city = query.city.strip() or None if query.city is not None else None
        wishes = query.wishes.strip() or None if query.wishes is not None else None
        rows = await self.items.list_affordable(
            query.budget,
            currency=currency,
            organization_type_id=query.organization_type_id,
            city=city,
            wishes=wishes,
        )
        grouped: dict[UUID, tuple[Organization, list[CatalogItem]]] = {}
        for organization, item in rows:
            grouped.setdefault(organization.id, (organization, []))[1].append(item)

        recommendations: list[BudgetRecommendation] = []
        party_size = query.party_size or 1
        for organization, available_items in grouped.values():
            selected: list[CatalogItem] = []
            total = Decimal("0")
            for item in available_items[:5] if query.budget is None else available_items:
                item_total = item.total_for(party_size)
                if query.budget is None or total + item_total <= query.budget:
                    selected.append(item)
                    total += item_total
            if selected:
                recommendations.append(
                    BudgetRecommendation(
                        organization=organization,
                        suggested_items=tuple(selected),
                        total=total,
                        remaining_budget=(
                            query.budget - total if query.budget is not None else None
                        ),
                    )
                )
        recommendations.sort(
            key=lambda recommendation: (
                recommendation.remaining_budget is None,
                recommendation.remaining_budget or Decimal("0"),
            )
        )
        return recommendations[: query.limit]
