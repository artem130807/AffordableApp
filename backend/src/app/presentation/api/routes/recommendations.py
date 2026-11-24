from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.application.cqrs.recommendation_filters import (
    CreateRecommendationFilterCommand,
    CreateRecommendationFilterHandler,
    ListUserRecommendationFiltersHandler,
    ListUserRecommendationFiltersQuery,
)
from app.application.cqrs.recommendations import (
    FindAffordableOrganizationsHandler,
    FindAffordableOrganizationsQuery,
)
from app.presentation.api.dependencies import CurrentUser, OptionalCurrentUser, UnitOfWorkDep
from app.presentation.schemas.organizations import (
    RecommendationFilterCreateRequest,
    RecommendationFilterResponse,
    RecommendationResponse,
    RecommendationSearchResponse,
)

router = APIRouter()


@router.get("/recommendations", response_model=list[RecommendationResponse])
async def find_recommendations(
    unit_of_work: UnitOfWorkDep,
    budget: Annotated[Decimal, Query(gt=0)],
    party_size: Annotated[int, Query(gt=0, le=20)] = 1,
    currency: Annotated[str, Query(pattern=r"^[A-Z]{3}$")] = "RUB",
    organization_type_id: UUID | None = None,
    city: str | None = None,
    limit: Annotated[int, Query(gt=0, le=100)] = 20,
) -> list[RecommendationResponse]:
    results = await FindAffordableOrganizationsHandler(unit_of_work.items).handle(
        FindAffordableOrganizationsQuery(
            budget=budget,
            party_size=party_size,
            currency=currency,
            organization_type_id=organization_type_id,
            city=city,
            limit=limit,
        )
    )
    return [RecommendationResponse.model_validate(item) for item in results]


@router.post(
    "/recommendation-searches",
    response_model=RecommendationSearchResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_recommendation_search(
    payload: RecommendationFilterCreateRequest,
    user: OptionalCurrentUser,
    unit_of_work: UnitOfWorkDep,
) -> RecommendationSearchResponse:
    recommendation_filter = await CreateRecommendationFilterHandler(
        unit_of_work.recommendation_filters,
        unit_of_work.organization_types,
    ).handle(
        CreateRecommendationFilterCommand(
            user_id=user.id if user else None,
            **payload.model_dump(),
        )
    )
    recommendations = await FindAffordableOrganizationsHandler(unit_of_work.items).handle(
        FindAffordableOrganizationsQuery(
            budget=recommendation_filter.budget,
            party_size=recommendation_filter.party_size,
            currency=recommendation_filter.currency,
            organization_type_id=recommendation_filter.organization_type_id,
            city=recommendation_filter.city,
            wishes=recommendation_filter.wishes,
        )
    )
    return RecommendationSearchResponse(
        filter=RecommendationFilterResponse.model_validate(recommendation_filter),
        recommendations=[RecommendationResponse.model_validate(item) for item in recommendations],
    )


@router.get(
    "/recommendation-filters/me",
    response_model=list[RecommendationFilterResponse],
)
async def list_my_recommendation_filters(
    user: CurrentUser,
    unit_of_work: UnitOfWorkDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[RecommendationFilterResponse]:
    filters = await ListUserRecommendationFiltersHandler(
        unit_of_work.recommendation_filters
    ).handle(
        ListUserRecommendationFiltersQuery(
            user_id=user.id,
            offset=offset,
            limit=limit,
        )
    )
    return [RecommendationFilterResponse.model_validate(item) for item in filters]
