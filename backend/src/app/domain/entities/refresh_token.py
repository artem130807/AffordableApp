from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass(slots=True)
class RefreshToken:
    user_id: UUID
    token_hash: str
    expires_at: datetime
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    revoked_at: datetime | None = None
    replaced_by_token_id: UUID | None = None
    user_agent: str | None = None
    ip_address: str | None = None

    @property
    def is_active(self) -> bool:
        return self.revoked_at is None and self.expires_at > datetime.now(UTC)

    def revoke(self, *, replaced_by_token_id: UUID | None = None) -> None:
        self.revoked_at = datetime.now(UTC)
        self.replaced_by_token_id = replaced_by_token_id
