import asyncio
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.application.cqrs.recommendation_filters import (
    CreateRecommendationFilterCommand,
    CreateRecommendationFilterHandler,
    ListUserRecommendationFiltersHandler,
    ListUserRecommendationFiltersQuery,
)
from app.domain.exceptions import ValidationError
from app.infrastructure.orm.models import Base
from app.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


def test_recommendation_filter_is_normalized_persisted_and_listed_for_user() -> None:
    asyncio.run(_verify_recommendation_filter_persistence())


async def _verify_recommendation_filter_persistence() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    user_id = uuid4()
    client_id = uuid4()
    async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        created = await CreateRecommendationFilterHandler(
            unit_of_work.recommendation_filters
        ).handle(
            CreateRecommendationFilterCommand(
                client_id=client_id,
                user_id=user_id,
                budget=Decimal("3500.00"),
                party_size=2,
                city="  Астрахань  ",
                wishes="   ",
            )
        )
        await unit_of_work.commit()

    assert created.city == "Астрахань"
    assert created.wishes is None
    assert created.currency == "RUB"

    async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        history = await ListUserRecommendationFiltersHandler(
            unit_of_work.recommendation_filters
        ).handle(ListUserRecommendationFiltersQuery(user_id=user_id))

    assert [item.id for item in history] == [created.id]
    assert history[0].client_id == client_id
    await engine.dispose()


@pytest.mark.parametrize(
    ("budget", "party_size"),
    [
        (Decimal("-0.01"), 2),
        (Decimal("1000"), 0),
        (Decimal("1000"), 21),
    ],
)
def test_recommendation_filter_rejects_invalid_numeric_answers(
    budget: Decimal,
    party_size: int,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
            with pytest.raises(ValidationError):
                await CreateRecommendationFilterHandler(unit_of_work.recommendation_filters).handle(
                    CreateRecommendationFilterCommand(
                        client_id=uuid4(),
                        budget=budget,
                        party_size=party_size,
                    )
                )
        await engine.dispose()

    asyncio.run(scenario())
