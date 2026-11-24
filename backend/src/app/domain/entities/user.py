from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.domain.entities.role import Role


@dataclass(slots=True)
class User:
    email: str
    name: str
    password_hash: str
    id: UUID = field(default_factory=uuid4)
    is_active: bool = True
    roles: list[Role] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def permissions(self) -> frozenset[str]:
        return frozenset(code for role in self.roles for code in role.permission_codes)

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions
