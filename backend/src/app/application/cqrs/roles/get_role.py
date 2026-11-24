from dataclasses import dataclass
from uuid import UUID

from app.domain.entities import Role
from app.domain.exceptions import NotFoundError
from app.domain.repositories import RoleRepository


@dataclass(frozen=True, slots=True)
class GetRoleQuery:
    role_id: UUID


class GetRoleHandler:
    def __init__(self, roles: RoleRepository) -> None:
        self.roles = roles

    async def handle(self, query: GetRoleQuery) -> Role:
        role = await self.roles.get(query.role_id)
        if role is None:
            raise NotFoundError("Роль не найдена")
        return role
