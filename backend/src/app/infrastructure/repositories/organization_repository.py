from collections.abc import Sequence
from dataclasses import asdict
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Organization
from app.infrastructure.orm.models import OrganizationModel


def organization_to_domain(model: OrganizationModel) -> Organization:
    return Organization(
        id=model.id,
        type_id=model.type_id,
        owner_id=model.owner_id,
        name=model.name,
        description=model.description,
        address=model.address,
        city=model.city,
        latitude=model.latitude,
        longitude=model.longitude,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SqlAlchemyOrganizationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, organization: Organization) -> Organization:
        model = OrganizationModel(**asdict(organization))
        self.session.add(model)
        await self.session.flush()
        return organization_to_domain(model)

    async def get(self, organization_id: UUID) -> Organization | None:
        model = await self.session.get(OrganizationModel, organization_id)
        return organization_to_domain(model) if model else None

    async def list(
        self,
        *,
        type_id: UUID | None = None,
        owner_id: UUID | None = None,
        city: str | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[Organization]:
        query = select(OrganizationModel).where(OrganizationModel.is_active.is_(True))
        if type_id:
            query = query.where(OrganizationModel.type_id == type_id)
        if owner_id:
            query = query.where(OrganizationModel.owner_id == owner_id)
        if city:
            query = query.where(func.lower(OrganizationModel.city) == city.lower())
        result = await self.session.scalars(
            query.order_by(OrganizationModel.name).offset(offset).limit(limit)
        )
        return [organization_to_domain(model) for model in result]
