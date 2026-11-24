from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities import PriceUnit


class RequestModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class OrganizationTypeCreateRequest(RequestModel):
    code: str = Field(pattern=r"^[a-z0-9_\-]+$", max_length=64)
    name: str = Field(min_length=2, max_length=120)
    description: str | None = None


class OrganizationTypeResponse(OrganizationTypeCreateRequest):
    id: UUID

    model_config = {"from_attributes": True}


class OrganizationCreateRequest(RequestModel):
    type_id: UUID
    name: str = Field(min_length=2, max_length=180)
    description: str | None = None
    address: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=120)
    latitude: Decimal | None = Field(default=None, ge=-90, le=90)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180)


class OrganizationResponse(OrganizationCreateRequest):
    id: UUID
    owner_id: UUID
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CatalogCreateRequest(RequestModel):
    name: str = Field(min_length=1, max_length=180)
    description: str | None = None


class CatalogResponse(CatalogCreateRequest):
    id: UUID
    organization_id: UUID
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CategoryCreateRequest(RequestModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None


class CategoryResponse(CategoryCreateRequest):
    id: UUID
    catalog_id: UUID

    model_config = {"from_attributes": True}


class CatalogItemCreateRequest(RequestModel):
    name: str = Field(min_length=1, max_length=180)
    price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    category_id: UUID | None = None
    description: str | None = None
    currency: str = Field(default="RUB", pattern=r"^[A-Z]{3}$")
    price_unit: PriceUnit = PriceUnit.ITEM
    attributes: dict[str, Any] = Field(default_factory=dict)


class CatalogItemResponse(CatalogItemCreateRequest):
    id: UUID
    catalog_id: UUID
    is_available: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class RecommendationResponse(BaseModel):
    organization: OrganizationResponse
    suggested_items: tuple[CatalogItemResponse, ...]
    total: Decimal
    remaining_budget: Decimal | None

    model_config = {"from_attributes": True}


class RecommendationFilterCreateRequest(RequestModel):
    client_id: UUID
    organization_type_id: UUID | None = None
    budget: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    party_size: int | None = Field(default=None, ge=1, le=20)
    city: str | None = Field(default=None, max_length=120)
    wishes: str | None = Field(default=None, max_length=500)
    currency: str = Field(default="RUB", pattern=r"^[A-Z]{3}$")


class RecommendationFilterResponse(RecommendationFilterCreateRequest):
    id: UUID
    user_id: UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


class RecommendationSearchResponse(BaseModel):
    filter: RecommendationFilterResponse
    recommendations: list[RecommendationResponse]
