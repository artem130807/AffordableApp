from app.domain.entities import OrganizationType
from app.domain.repositories import OrganizationTypeRepository


class ListOrganizationTypesHandler:
    def __init__(self, types: OrganizationTypeRepository) -> None:
        self.types = types

    async def handle(self) -> list[OrganizationType]:
        return list(await self.types.list())
