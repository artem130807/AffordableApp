from collections.abc import AsyncIterator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports import PasswordHasherPort, TokenServicePort, UnitOfWork
from app.application.use_cases import CheckReadiness, GetServiceStatus
from app.domain.entities import User
from app.domain.exceptions import (
    AuthenticationError,
    PermissionDeniedError,
    RefreshTokenReuseError,
)
from app.infrastructure.config import Settings, get_settings
from app.infrastructure.database import async_session_factory, get_session
from app.infrastructure.health import SqlAlchemyDatabaseHealth
from app.infrastructure.security import PasswordHasher, TokenService
from app.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


def provide_service_status_use_case(
    settings: Annotated[Settings, Depends(get_settings)],
) -> GetServiceStatus:
    return GetServiceStatus(
        service_name=settings.app_name,
        environment=settings.app_env,
    )


ServiceStatusUseCase = Annotated[
    GetServiceStatus,
    Depends(provide_service_status_use_case),
]

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def provide_readiness_use_case(
    session: SessionDep,
    settings: Annotated[Settings, Depends(get_settings)],
) -> CheckReadiness:
    return CheckReadiness(
        SqlAlchemyDatabaseHealth(session),
        service_name=settings.app_name,
        environment=settings.app_env,
    )


ReadinessUseCase = Annotated[CheckReadiness, Depends(provide_readiness_use_case)]


async def provide_unit_of_work() -> AsyncIterator[UnitOfWork]:
    async with SqlAlchemyUnitOfWork(async_session_factory) as unit_of_work:
        try:
            yield unit_of_work
            await unit_of_work.commit()
        except RefreshTokenReuseError:
            # Reuse detection revokes the whole token family and must be persisted.
            await unit_of_work.commit()
            raise
        except BaseException:
            await unit_of_work.rollback()
            raise


UnitOfWorkDep = Annotated[UnitOfWork, Depends(provide_unit_of_work)]
bearer_scheme = HTTPBearer(auto_error=False)


def provide_token_service(settings: Annotated[Settings, Depends(get_settings)]) -> TokenService:
    return TokenService(settings)


def provide_password_hasher() -> PasswordHasher:
    return PasswordHasher()


TokenServiceDep = Annotated[TokenServicePort, Depends(provide_token_service)]
PasswordHasherDep = Annotated[PasswordHasherPort, Depends(provide_password_hasher)]


async def get_current_user(
    unit_of_work: UnitOfWorkDep,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Security(bearer_scheme),
    ],
    token_service: Annotated[TokenService, Depends(provide_token_service)],
) -> User:
    user = await _resolve_user(unit_of_work, credentials, token_service)
    if user is None:
        raise AuthenticationError("Требуется авторизация")
    return user


async def get_optional_current_user(
    unit_of_work: UnitOfWorkDep,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Security(bearer_scheme),
    ],
    token_service: Annotated[TokenService, Depends(provide_token_service)],
) -> User | None:
    return await _resolve_user(unit_of_work, credentials, token_service)


async def _resolve_user(
    unit_of_work: UnitOfWork,
    credentials: HTTPAuthorizationCredentials | None,
    token_service: TokenService,
) -> User | None:
    if credentials is None:
        return None
    payload = token_service.decode_access_token(credentials.credentials)
    try:
        user_id = UUID(str(payload["sub"]))
    except (KeyError, ValueError) as error:
        raise AuthenticationError("Некорректный идентификатор пользователя") from error
    user = await unit_of_work.users.get(user_id)
    if user is None or not user.is_active:
        raise AuthenticationError("Пользователь не найден или заблокирован")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalCurrentUser = Annotated[User | None, Depends(get_optional_current_user)]


class RequirePermission:
    def __init__(self, permission: str) -> None:
        self.permission = permission

    async def __call__(self, user: CurrentUser) -> User:
        if not user.has_permission(self.permission):
            raise PermissionDeniedError(f"Недостаточно прав: требуется {self.permission}")
        return user


def permission_policy(permission: str) -> RequirePermission:
    return RequirePermission(permission)
