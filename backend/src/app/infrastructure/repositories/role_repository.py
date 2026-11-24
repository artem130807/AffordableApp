from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities import Role
from app.infrastructure.orm.models import PermissionModel, RoleModel
from app.infrastructure.repositories.permission_repository import permission_to_domain


def role_to_domain(model: RoleModel) -> Role:
    return Role(
        id=model.id,
        name=model.name,
        description=model.description,
        permissions=tuple(permission_to_domain(permission) for permission in model.permissions),
        created_at=model.created_at,
    )


class SqlAlchemyRoleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, role: Role) -> Role:
        permission_models: list[PermissionModel] = []
        if role.permissions:
            result = await self.session.scalars(
                select(PermissionModel).where(
                    PermissionModel.id.in_([permission.id for permission in role.permissions])
                )
            )
            permission_models = list(result)
        model = RoleModel(
            id=role.id,
            name=role.name,
            description=role.description,
            permissions=permission_models,
            created_at=role.created_at,
        )
        self.session.add(model)
        await self.session.flush()
        return role_to_domain(model)

    async def get(self, role_id: UUID) -> Role | None:
        model = await self.session.scalar(
            select(RoleModel)
            .where(RoleModel.id == role_id)
            .options(selectinload(RoleModel.permissions))
        )
        return role_to_domain(model) if model else None

    async def get_by_name(self, name: str) -> Role | None:
        model = await self.session.scalar(
            select(RoleModel)
            .where(RoleModel.name == name.lower())
            .options(selectinload(RoleModel.permissions))
        )
        return role_to_domain(model) if model else None

    async def list(self) -> Sequence[Role]:
        result = await self.session.scalars(
            select(RoleModel).options(selectinload(RoleModel.permissions)).order_by(RoleModel.name)
        )
        return [role_to_domain(model) for model in result]

    async def assign_permission(self, role_id: UUID, permission_id: UUID) -> Role | None:
        model = await self.session.scalar(
            select(RoleModel)
            .where(RoleModel.id == role_id)
            .options(selectinload(RoleModel.permissions))
        )
        permission = await self.session.get(PermissionModel, permission_id)
        if model is None or permission is None:
            return None
        if permission not in model.permissions:
            model.permissions.append(permission)
            await self.session.flush()
        return role_to_domain(model)
