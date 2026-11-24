from dataclasses import dataclass
from uuid import UUID

from app.domain.entities import User
from app.domain.exceptions import NotFoundError
from app.domain.repositories import RoleRepository, UserRepository


@dataclass(frozen=True, slots=True)
class AssignRoleToUserCommand:
    user_id: UUID
    role_id: UUID


class AssignRoleToUserHandler:
    def __init__(self, users: UserRepository, roles: RoleRepository) -> None:
        self.users = users
        self.roles = roles

    async def handle(self, command: AssignRoleToUserCommand) -> User:
        if await self.roles.get(command.role_id) is None:
            raise NotFoundError("Роль не найдена")
        user = await self.users.assign_role(command.user_id, command.role_id)
        if user is None:
            raise NotFoundError("Пользователь не найден")
        return user
