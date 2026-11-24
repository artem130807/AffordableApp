from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Permission
from app.infrastructure.orm.models import PermissionModel


def permission_to_domain(model: PermissionModel) -> Permission:
    return Permission(
        id=model.id,
        code=model.code,
        name=model.name,
        description=model.description,
        created_at=model.created_at,
    )


class SqlAlchemyPermissionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, permission: Permission) -> Permission:
        model = PermissionModel(
            id=permission.id,
            code=permission.code,
            name=permission.name,
            description=permission.description,
            created_at=permission.created_at,
        )
        self.session.add(model)
        await self.session.flush()
        return permission_to_domain(model)

    async def get(self, permission_id: UUID) -> Permission | None:
        model = await self.session.get(PermissionModel, permission_id)
        return permission_to_domain(model) if model else None

    async def get_by_code(self, code: str) -> Permission | None:
        model = await self.session.scalar(
            select(PermissionModel).where(PermissionModel.code == code)
        )
        return permission_to_domain(model) if model else None

    async def list(self) -> Sequence[Permission]:
        result = await self.session.scalars(select(PermissionModel).order_by(PermissionModel.code))
        return [permission_to_domain(model) for model in result]

    async def get_many_by_codes(self, codes: frozenset[str]) -> Sequence[Permission]:
        if not codes:
            return []
        result = await self.session.scalars(
            select(PermissionModel)
            .where(PermissionModel.code.in_(codes))
            .order_by(PermissionModel.code)
        )
        return [permission_to_domain(model) for model in result]
