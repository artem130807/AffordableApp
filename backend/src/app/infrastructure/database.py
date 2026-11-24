from collections.abc import AsyncIterator

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

from app.domain.entities import OrganizationType, Permission, Role, User
from app.domain.permissions import (
    ADMIN_PERMISSIONS,
    DEFAULT_USER_PERMISSIONS,
    SYSTEM_PERMISSION_NAMES,
)
from app.infrastructure.config import get_settings
from app.infrastructure.orm.models import Base, PermissionModel, RoleModel

settings = get_settings()
engine = create_async_engine(settings.database_url, pool_pre_ping=True)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_session_factory() as session:
        yield session


async def initialize_database() -> None:
    if settings.auto_create_schema:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    from app.infrastructure.repositories import (
        SqlAlchemyOrganizationTypeRepository,
        SqlAlchemyPermissionRepository,
        SqlAlchemyRoleRepository,
        SqlAlchemyUserRepository,
    )
    from app.infrastructure.security import PasswordHasher

    async with async_session_factory() as session:
        if session.bind and session.bind.dialect.name == "postgresql":
            await session.execute(text("SELECT pg_advisory_xact_lock(17420189)"))
        roles = SqlAlchemyRoleRepository(session)
        types = SqlAlchemyOrganizationTypeRepository(session)
        users = SqlAlchemyUserRepository(session)
        permissions = SqlAlchemyPermissionRepository(session)

        system_permissions: dict[str, Permission] = {}
        for code, name in SYSTEM_PERMISSION_NAMES.items():
            permission = await permissions.get_by_code(code.value)
            if permission is None:
                permission = await permissions.add(Permission(code=code.value, name=name))
            system_permissions[code.value] = permission

        async def ensure_role_permissions(role: Role, codes: frozenset[str]) -> Role:
            model = await session.scalar(
                select(RoleModel)
                .where(RoleModel.id == role.id)
                .options(selectinload(RoleModel.permissions))
            )
            permission_models = list(
                await session.scalars(
                    select(PermissionModel).where(PermissionModel.code.in_(codes))
                )
            )
            if model is not None:
                existing_ids = {permission.id for permission in model.permissions}
                model.permissions.extend(
                    permission
                    for permission in permission_models
                    if permission.id not in existing_ids
                )
                await session.flush()
                refreshed = await roles.get(role.id)
                if refreshed is not None:
                    return refreshed
            return role

        user_role = await roles.get_by_name("user")
        if user_role is None:
            user_role = await roles.add(
                Role(
                    name="user",
                    description="Обычный пользователь",
                    permissions=tuple(
                        system_permissions[code] for code in DEFAULT_USER_PERMISSIONS
                    ),
                )
            )
        elif not DEFAULT_USER_PERMISSIONS.issubset(user_role.permission_codes):
            user_role = await ensure_role_permissions(user_role, DEFAULT_USER_PERMISSIONS)

        admin_role = await roles.get_by_name("admin")
        if admin_role is None:
            admin_role = await roles.add(
                Role(
                    name="admin",
                    description="Администратор платформы",
                    permissions=tuple(system_permissions[code] for code in ADMIN_PERMISSIONS),
                )
            )
        elif not ADMIN_PERMISSIONS.issubset(admin_role.permission_codes):
            admin_role = await ensure_role_permissions(admin_role, ADMIN_PERMISSIONS)

        if settings.bootstrap_admin_email and settings.bootstrap_admin_password:
            existing_admin = await users.get_by_email(settings.bootstrap_admin_email)
            if existing_admin is None:
                await users.add(
                    User(
                        email=settings.bootstrap_admin_email.lower(),
                        name="Administrator",
                        password_hash=PasswordHasher().hash(settings.bootstrap_admin_password),
                        roles=[admin_role],
                    )
                )

        default_types = (
            ("restaurant", "Ресторан"),
            ("theater", "Театр"),
            ("electronics_store", "Магазин электроники"),
            ("entertainment", "Развлечения"),
        )
        for organization_type_code, organization_type_name in default_types:
            if await types.get_by_code(organization_type_code) is None:
                await types.add(
                    OrganizationType(
                        code=organization_type_code,
                        name=organization_type_name,
                    )
                )
        await session.commit()


async def close_database() -> None:
    await engine.dispose()
