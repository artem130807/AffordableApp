import asyncio
from collections.abc import Sequence
from decimal import Decimal
from typing import cast
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.application.cqrs.recommendations import (
    FindAffordableOrganizationsHandler,
    FindAffordableOrganizationsQuery,
)
from app.domain.entities import CatalogItem, Organization, PriceUnit
from app.domain.repositories import CatalogItemRepository
from app.infrastructure.database import async_session_factory
from app.infrastructure.orm.models import RecommendationFilterModel
from app.infrastructure.repositories import SqlAlchemyCatalogItemRepository
from app.main import app


class RecordingCatalogItems:
    def __init__(self) -> None:
        self.received_budget: Decimal | None = Decimal("-1")
        self.received_city: str | None = None
        self.received_wishes: str | None = None

    async def list_affordable(
        self,
        budget: Decimal | None,
        *,
        currency: str,
        organization_type_id: UUID | None = None,
        city: str | None = None,
        wishes: str | None = None,
    ) -> Sequence[tuple[Organization, CatalogItem]]:
        self.received_budget = budget
        self.received_city = city
        self.received_wishes = wishes
        return []


class StaticCatalogItems(RecordingCatalogItems):
    def __init__(self, rows: Sequence[tuple[Organization, CatalogItem]]) -> None:
        super().__init__()
        self.rows = rows

    async def list_affordable(
        self,
        budget: Decimal | None,
        *,
        currency: str,
        organization_type_id: UUID | None = None,
        city: str | None = None,
        wishes: str | None = None,
    ) -> Sequence[tuple[Organization, CatalogItem]]:
        await super().list_affordable(
            budget,
            currency=currency,
            organization_type_id=organization_type_id,
            city=city,
            wishes=wishes,
        )
        return self.rows


def test_recommendation_query_allows_skipped_budget_and_forwards_wishes() -> None:
    async def scenario() -> None:
        items = RecordingCatalogItems()
        result = await FindAffordableOrganizationsHandler(
            cast(CatalogItemRepository, items)
        ).handle(
            FindAffordableOrganizationsQuery(
                budget=None,
                wishes="тихое место",
            )
        )
        assert result == []
        assert items.received_budget is None
        assert items.received_wishes == "тихое место"

    asyncio.run(scenario())


def test_recommendation_query_normalizes_optional_text_filters() -> None:
    async def scenario() -> None:
        items = RecordingCatalogItems()
        await FindAffordableOrganizationsHandler(cast(CatalogItemRepository, items)).handle(
            FindAffordableOrganizationsQuery(
                budget=Decimal("1000"),
                city="  Астрахань  ",
                wishes="   ",
            )
        )
        assert items.received_city == "Астрахань"
        assert items.received_wishes is None

    asyncio.run(scenario())


@pytest.mark.parametrize("price_unit", [PriceUnit.PERSON, PriceUnit.TICKET])
def test_per_visitor_price_is_calculated_for_every_visitor(price_unit: PriceUnit) -> None:
    item = CatalogItem(
        catalog_id=uuid4(),
        name="Билет",
        price=Decimal("500"),
        price_unit=price_unit,
    )

    assert item.total_for(3) == Decimal("1500")


def test_zero_budget_returns_only_free_items() -> None:
    async def scenario() -> None:
        organization = Organization(type_id=uuid4(), owner_id=uuid4(), name="Музей")
        free = CatalogItem(catalog_id=uuid4(), name="Свободный вход", price=Decimal("0"))
        paid = CatalogItem(catalog_id=uuid4(), name="Экскурсия", price=Decimal("500"))
        items = StaticCatalogItems([(organization, free), (organization, paid)])

        result = await FindAffordableOrganizationsHandler(
            cast(CatalogItemRepository, items)
        ).handle(FindAffordableOrganizationsQuery(budget=Decimal("0")))

        assert len(result) == 1
        assert result[0].suggested_items == (free,)
        assert result[0].total == Decimal("0")
        assert result[0].remaining_budget == Decimal("0")

    asyncio.run(scenario())


def test_recommendations_are_limited_after_closest_budget_match_sorting() -> None:
    async def scenario() -> None:
        first = Organization(type_id=uuid4(), owner_id=uuid4(), name="Первое место")
        closest = Organization(type_id=uuid4(), owner_id=uuid4(), name="Точное место")
        rows = [
            (first, CatalogItem(catalog_id=uuid4(), name="Дешёвый вариант", price=Decimal("400"))),
            (closest, CatalogItem(catalog_id=uuid4(), name="Точный вариант", price=Decimal("900"))),
        ]

        result = await FindAffordableOrganizationsHandler(
            cast(CatalogItemRepository, StaticCatalogItems(rows))
        ).handle(FindAffordableOrganizationsQuery(budget=Decimal("1000"), limit=1))

        assert [recommendation.organization.id for recommendation in result] == [closest.id]

    asyncio.run(scenario())


def test_anonymous_skip_all_search_is_persisted_once() -> None:
    with TestClient(app) as client:
        client_id = str(uuid4())
        response = client.post(
            "/api/v1/recommendation-searches",
            json={"client_id": client_id},
        )

        assert response.status_code == 201, response.text
        body = response.json()
        assert body["filter"]["client_id"] == client_id
        assert body["filter"]["user_id"] is None
        assert body["filter"]["budget"] is None
        assert isinstance(body["recommendations"], list)


def test_authenticated_search_appears_in_current_user_history() -> None:
    with TestClient(app) as client:
        email = f"filter-{uuid4()}@example.com"
        register = client.post(
            "/api/v1/auth/register",
            json={"email": email, "name": "Filter User", "password": "strong-password"},
        )
        assert register.status_code == 201
        login = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "strong-password"},
        )
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        client_id = str(uuid4())

        search = client.post(
            "/api/v1/recommendation-searches",
            headers=headers,
            json={
                "client_id": client_id,
                "budget": "2500.00",
                "party_size": 2,
                "city": "Астрахань",
                "wishes": "Тихое место",
            },
        )
        assert search.status_code == 201, search.text

        history = client.get("/api/v1/recommendation-filters/me", headers=headers)
        assert history.status_code == 200, history.text
        assert history.json()[0]["id"] == search.json()["filter"]["id"]
        assert history.json()[0]["user_id"] == register.json()["id"]


def test_failed_recommendation_lookup_rolls_back_persisted_filter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client_id = uuid4()

    async def count_filters() -> int:
        async with async_session_factory() as session:
            return int(
                await session.scalar(
                    select(func.count()).select_from(RecommendationFilterModel).where(
                        RecommendationFilterModel.client_id == client_id
                    )
                )
                or 0
            )

    async def fail_lookup(*_: object, **__: object) -> Sequence[tuple[Organization, CatalogItem]]:
        raise RuntimeError("forced recommendation failure")

    monkeypatch.setattr(SqlAlchemyCatalogItemRepository, "list_affordable", fail_lookup)
    with TestClient(app) as client:
        with pytest.raises(RuntimeError, match="forced recommendation"):
            client.post(
                "/api/v1/recommendation-searches",
                json={"client_id": str(client_id), "budget": "1000.00"},
            )
        assert asyncio.run(count_filters()) == 0
