from app.domain.entities import Role
from app.domain.repositories import RoleRepository


class ListRolesHandler:
    def __init__(self, roles: RoleRepository) -> None:
        self.roles = roles

    async def handle(self) -> list[Role]:
        return list(await self.roles.list())
