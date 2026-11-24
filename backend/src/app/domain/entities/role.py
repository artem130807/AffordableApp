from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.domain.entities.permission import Permission


@dataclass(frozen=True, slots=True)
class Role:
    name: str
    permissions: tuple[Permission, ...]
    description: str | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def permission_codes(self) -> frozenset[str]:
        return frozenset(permission.code for permission in self.permissions)
