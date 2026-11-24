from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities import User
from app.infrastructure.orm.models import RoleModel, UserModel
from app.infrastructure.repositories.role_repository import role_to_domain


def user_to_domain(model: UserModel) -> User:
    return User(
        id=model.id,
        email=model.email,
        name=model.name,
        password_hash=model.password_hash,
        is_active=model.is_active,
        roles=[role_to_domain(role) for role in model.roles],
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


_ROLES_AND_PERMISSIONS = selectinload(UserModel.roles).selectinload(RoleModel.permissions)


class SqlAlchemyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, user: User) -> User:
        roles: list[RoleModel] = []
        if user.roles:
            result = await self.session.scalars(
                select(RoleModel)
                .where(RoleModel.id.in_([role.id for role in user.roles]))
                .options(selectinload(RoleModel.permissions))
            )
            roles = list(result)
        model = UserModel(
            id=user.id,
            email=user.email.lower(),
            name=user.name,
            password_hash=user.password_hash,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            roles=roles,
        )
        self.session.add(model)
        await self.session.flush()
        return user_to_domain(model)

    async def get(self, user_id: UUID) -> User | None:
        model = await self.session.scalar(
            select(UserModel).where(UserModel.id == user_id).options(_ROLES_AND_PERMISSIONS)
        )
        return user_to_domain(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        model = await self.session.scalar(
            select(UserModel)
            .where(UserModel.email == email.lower())
            .options(_ROLES_AND_PERMISSIONS)
        )
        return user_to_domain(model) if model else None

    async def list(self, *, offset: int = 0, limit: int = 100) -> Sequence[User]:
        result = await self.session.scalars(
            select(UserModel)
            .options(_ROLES_AND_PERMISSIONS)
            .order_by(UserModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return [user_to_domain(model) for model in result]

    async def assign_role(self, user_id: UUID, role_id: UUID) -> User | None:
        model = await self.session.scalar(
            select(UserModel).where(UserModel.id == user_id).options(_ROLES_AND_PERMISSIONS)
        )
        role = await self.session.scalar(
            select(RoleModel)
            .where(RoleModel.id == role_id)
            .options(selectinload(RoleModel.permissions))
        )
        if model is None or role is None:
            return None
        if role not in model.roles:
            model.roles.append(role)
            await self.session.flush()
        return user_to_domain(model)
