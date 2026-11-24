from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from math import ceil
from typing import Any
from uuid import UUID, uuid4


class PriceUnit(StrEnum):
    ITEM = "item"
    PERSON = "person"
    TICKET = "ticket"
    HOUR = "hour"
    SERVICE = "service"


@dataclass(slots=True)
class Catalog:
    organization_id: UUID
    name: str
    description: str | None = None
    id: UUID = field(default_factory=uuid4)
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(slots=True)
class ItemCategory:
    catalog_id: UUID
    name: str
    description: str | None = None
    id: UUID = field(default_factory=uuid4)


@dataclass(slots=True)
class CatalogItem:
    catalog_id: UUID
    name: str
    price: Decimal
    category_id: UUID | None = None
    description: str | None = None
    currency: str = "RUB"
    price_unit: PriceUnit = PriceUnit.ITEM
    attributes: dict[str, Any] = field(default_factory=dict)
    id: UUID = field(default_factory=uuid4)
    is_available: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def total_for(self, party_size: int) -> Decimal:
        multiplier = 1
        if self.price_unit in {PriceUnit.PERSON, PriceUnit.TICKET}:
            multiplier = party_size
        elif self.price_unit == PriceUnit.ITEM:
            serves = self.attributes.get("serves")
            if isinstance(serves, int) and not isinstance(serves, bool) and serves > 0:
                multiplier = ceil(party_size / serves)
        return self.price * multiplier
