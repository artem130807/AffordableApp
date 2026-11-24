from dataclasses import dataclass
from uuid import UUID

from app.domain.entities import Organization
from app.domain.exceptions import ValidationError
from app.domain.repositories import OrganizationRepository


@dataclass(frozen=True, slots=True)
class ListOrganizationsQuery:
    type_id: UUID | None = None
    owner_id: UUID | None = None
    city: str | None = None
    offset: int = 0
    limit: int = 100


class ListOrganizationsHandler:
    def __init__(self, organizations: OrganizationRepository) -> None:
        self.organizations = organizations

    async def handle(self, query: ListOrganizationsQuery) -> list[Organization]:
        if query.offset < 0 or not 1 <= query.limit <= 100:
            raise ValidationError("Некорректные параметры пагинации")
        city = query.city.strip() or None if query.city is not None else None
        return list(
            await self.organizations.list(
                type_id=query.type_id,
                owner_id=query.owner_id,
                city=city,
                offset=query.offset,
                limit=query.limit,
            )
        )
