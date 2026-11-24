from dataclasses import dataclass
from uuid import UUID

from app.domain.entities import OrganizationType
from app.domain.exceptions import NotFoundError
from app.domain.repositories import OrganizationTypeRepository


@dataclass(frozen=True, slots=True)
class GetOrganizationTypeQuery:
    type_id: UUID


class GetOrganizationTypeHandler:
    def __init__(self, types: OrganizationTypeRepository) -> None:
        self.types = types

    async def handle(self, query: GetOrganizationTypeQuery) -> OrganizationType:
        result = await self.types.get(query.type_id)
        if result is None:
            raise NotFoundError("Тип организации не найден")
        return result
