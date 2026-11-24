from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.repositories import (
    SqlAlchemyCatalogItemRepository,
    SqlAlchemyCatalogRepository,
    SqlAlchemyItemCategoryRepository,
    SqlAlchemyOrganizationRepository,
    SqlAlchemyOrganizationTypeRepository,
    SqlAlchemyPermissionRepository,
    SqlAlchemyRecommendationFilterRepository,
    SqlAlchemyRefreshTokenRepository,
    SqlAlchemyRoleRepository,
    SqlAlchemyUserRepository,
)


class SqlAlchemyUnitOfWork:
    """Owns one SQLAlchemy session and all repositories participating in its transaction."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session = session_factory()
        self._completed = False

        self.users = SqlAlchemyUserRepository(self._session)
        self.roles = SqlAlchemyRoleRepository(self._session)
        self.permissions = SqlAlchemyPermissionRepository(self._session)
        self.organization_types = SqlAlchemyOrganizationTypeRepository(self._session)
        self.organizations = SqlAlchemyOrganizationRepository(self._session)
        self.catalogs = SqlAlchemyCatalogRepository(self._session)
        self.categories = SqlAlchemyItemCategoryRepository(self._session)
        self.items = SqlAlchemyCatalogItemRepository(self._session)
        self.refresh_tokens = SqlAlchemyRefreshTokenRepository(self._session)
        self.recommendation_filters = SqlAlchemyRecommendationFilterRepository(self._session)

    @property
    def session(self) -> AsyncSession:
        """Infrastructure-only access for health checks and bootstrap tasks."""
        return self._session

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if not self._completed:
            await self.rollback()
        await self._session.close()

    async def commit(self) -> None:
        await self._session.commit()
        self._completed = True

    async def rollback(self) -> None:
        await self._session.rollback()
        self._completed = True
