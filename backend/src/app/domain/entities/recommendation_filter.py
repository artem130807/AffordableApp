from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class RecommendationFilter:
    client_id: UUID
    user_id: UUID | None = None
    organization_type_id: UUID | None = None
    budget: Decimal | None = None
    party_size: int | None = None
    city: str | None = None
    wishes: str | None = None
    currency: str = "RUB"
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
