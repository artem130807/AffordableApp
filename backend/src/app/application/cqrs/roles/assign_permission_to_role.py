from dataclasses import dataclass
from uuid import UUID

from app.domain.entities import Role
from app.domain.exceptions import NotFoundError
from app.domain.repositories import PermissionRepository, RoleRepository


@dataclass(frozen=True, slots=True)
class AssignPermissionToRoleCommand:
    role_id: UUID
    permission_id: UUID


class AssignPermissionToRoleHandler:
    def __init__(self, roles: RoleRepository, permissions: PermissionRepository) -> None:
        self.roles = roles
        self.permissions = permissions

    async def handle(self, command: AssignPermissionToRoleCommand) -> Role:
        if await self.permissions.get(command.permission_id) is None:
            raise NotFoundError("Право не найдено")
        role = await self.roles.assign_permission(command.role_id, command.permission_id)
        if role is None:
            raise NotFoundError("Роль не найдена")
        return role
