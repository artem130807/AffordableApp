from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from app.domain.entities import Organization
from app.domain.exceptions import NotFoundError, ValidationError
from app.domain.repositories import OrganizationRepository, OrganizationTypeRepository
from app.domain.validation import normalize_required_text


@dataclass(frozen=True, slots=True)
class CreateOrganizationCommand:
    type_id: UUID
    owner_id: UUID
    name: str
    description: str | None = None
    address: str | None = None
    city: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None


class CreateOrganizationHandler:
    def __init__(
        self,
        organizations: OrganizationRepository,
        types: OrganizationTypeRepository,
    ) -> None:
        self.organizations = organizations
        self.types = types

    async def handle(self, command: CreateOrganizationCommand) -> Organization:
        if await self.types.get(command.type_id) is None:
            raise NotFoundError("Тип организации не найден")
        if command.latitude is not None and not Decimal("-90") <= command.latitude <= Decimal("90"):
            raise ValidationError("Широта должна находиться в диапазоне от -90 до 90")
        if command.longitude is not None and not Decimal("-180") <= command.longitude <= Decimal(
            "180"
        ):
            raise ValidationError("Долгота должна находиться в диапазоне от -180 до 180")
        name = normalize_required_text(
            command.name,
            field_name="Название организации",
            min_length=2,
            max_length=180,
        )
        return await self.organizations.add(
            Organization(
                type_id=command.type_id,
                owner_id=command.owner_id,
                name=name,
                description=command.description,
                address=command.address,
                city=command.city,
                latitude=command.latitude,
                longitude=command.longitude,
            )
        )
