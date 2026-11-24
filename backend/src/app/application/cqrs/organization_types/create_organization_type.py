from dataclasses import dataclass

from app.domain.entities import OrganizationType
from app.domain.exceptions import ConflictError
from app.domain.repositories import OrganizationTypeRepository
from app.domain.validation import normalize_code, normalize_required_text


@dataclass(frozen=True, slots=True)
class CreateOrganizationTypeCommand:
    code: str
    name: str
    description: str | None = None


class CreateOrganizationTypeHandler:
    def __init__(self, types: OrganizationTypeRepository) -> None:
        self.types = types

    async def handle(self, command: CreateOrganizationTypeCommand) -> OrganizationType:
        code = normalize_code(
            command.code,
            pattern=r"[a-z0-9_-]+",
            field_name="Код типа организации",
            max_length=64,
        )
        name = normalize_required_text(
            command.name,
            field_name="Название типа организации",
            min_length=2,
            max_length=120,
        )
        if await self.types.get_by_code(code):
            raise ConflictError("Тип организации с таким кодом уже существует")
        return await self.types.add(
            OrganizationType(code=code, name=name, description=command.description)
        )
