from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class OrganizationType:
    code: str
    name: str
    description: str | None = None
    id: UUID = field(default_factory=uuid4)


@dataclass(slots=True)
class Organization:
    type_id: UUID
    owner_id: UUID
    name: str
    description: str | None = None
    address: str | None = None
    city: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    id: UUID = field(default_factory=uuid4)
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
