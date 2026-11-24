from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import OrganizationType
from app.infrastructure.orm.models import OrganizationTypeModel


def organization_type_to_domain(model: OrganizationTypeModel) -> OrganizationType:
    return OrganizationType(
        id=model.id,
        code=model.code,
        name=model.name,
        description=model.description,
    )


class SqlAlchemyOrganizationTypeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, organization_type: OrganizationType) -> OrganizationType:
        model = OrganizationTypeModel(
            id=organization_type.id,
            code=organization_type.code,
            name=organization_type.name,
            description=organization_type.description,
        )
        self.session.add(model)
        await self.session.flush()
        return organization_type_to_domain(model)

    async def get(self, type_id: UUID) -> OrganizationType | None:
        model = await self.session.get(OrganizationTypeModel, type_id)
        return organization_type_to_domain(model) if model else None

    async def get_by_code(self, code: str) -> OrganizationType | None:
        model = await self.session.scalar(
            select(OrganizationTypeModel).where(OrganizationTypeModel.code == code)
        )
        return organization_type_to_domain(model) if model else None

    async def list(self) -> Sequence[OrganizationType]:
        result = await self.session.scalars(
            select(OrganizationTypeModel).order_by(OrganizationTypeModel.name)
        )
        return [organization_type_to_domain(model) for model in result]
