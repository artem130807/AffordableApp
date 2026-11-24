from dataclasses import dataclass

from app.domain.entities import Permission
from app.domain.exceptions import ConflictError
from app.domain.repositories import PermissionRepository
from app.domain.validation import normalize_code, normalize_required_text


@dataclass(frozen=True, slots=True)
class CreatePermissionCommand:
    code: str
    name: str
    description: str | None = None


class CreatePermissionHandler:
    def __init__(self, permissions: PermissionRepository) -> None:
        self.permissions = permissions

    async def handle(self, command: CreatePermissionCommand) -> Permission:
        code = normalize_code(
            command.code,
            pattern=r"[a-z][a-z0-9_.:-]*",
            field_name="Код права",
            max_length=100,
        )
        name = normalize_required_text(
            command.name,
            field_name="Название права",
            min_length=2,
            max_length=150,
        )
        if await self.permissions.get_by_code(code):
            raise ConflictError("Право с таким кодом уже существует")
        return await self.permissions.add(
            Permission(code=code, name=name, description=command.description)
        )
