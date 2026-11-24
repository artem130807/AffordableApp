from dataclasses import dataclass

from app.domain.entities import Role
from app.domain.exceptions import ConflictError, ValidationError
from app.domain.repositories import PermissionRepository, RoleRepository
from app.domain.validation import normalize_code


@dataclass(frozen=True, slots=True)
class CreateRoleCommand:
    name: str
    permissions: frozenset[str]
    description: str | None = None


class CreateRoleHandler:
    def __init__(self, roles: RoleRepository, permissions: PermissionRepository) -> None:
        self.roles = roles
        self.permissions = permissions

    async def handle(self, command: CreateRoleCommand) -> Role:
        name = normalize_code(
            command.name,
            pattern=r"[a-z][a-z0-9_-]*",
            field_name="Название роли",
            max_length=64,
        )
        if await self.roles.get_by_name(name):
            raise ConflictError("Роль с таким именем уже существует")
        permissions = await self.permissions.get_many_by_codes(command.permissions)
        found_codes = frozenset(permission.code for permission in permissions)
        unknown = command.permissions - found_codes
        if unknown:
            raise ValidationError(f"Неизвестные права: {', '.join(sorted(unknown))}")
        return await self.roles.add(
            Role(
                name=name,
                permissions=tuple(permissions),
                description=command.description,
            )
        )
