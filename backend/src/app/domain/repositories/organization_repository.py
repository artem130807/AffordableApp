from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from app.domain.entities import Organization


class OrganizationRepository(Protocol):
    async def add(self, organization: Organization) -> Organization: ...
    async def get(self, organization_id: UUID) -> Organization | None: ...
    async def list(
        self,
        *,
        type_id: UUID | None = None,
        owner_id: UUID | None = None,
        city: str | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[Organization]: ...
