from dataclasses import dataclass
from uuid import UUID

from app.domain.entities import Organization
from app.domain.exceptions import NotFoundError
from app.domain.repositories import OrganizationRepository


@dataclass(frozen=True, slots=True)
class GetOrganizationQuery:
    organization_id: UUID


class GetOrganizationHandler:
    def __init__(self, organizations: OrganizationRepository) -> None:
        self.organizations = organizations

    async def handle(self, query: GetOrganizationQuery) -> Organization:
        organization = await self.organizations.get(query.organization_id)
        if organization is None:
            raise NotFoundError("Организация не найдена")
        return organization
