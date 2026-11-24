from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.domain.exceptions import (
    AuthenticationError,
    ConflictError,
    DomainError,
    NotFoundError,
    PermissionDeniedError,
    RefreshTokenReuseError,
    ServiceUnavailableError,
    ValidationError,
)
from app.infrastructure.config import get_settings
from app.infrastructure.database import close_database, initialize_database
from app.presentation.api.router import api_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await initialize_database()
    try:
        yield
    finally:
        await close_database()


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version="0.1.0",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(api_router, prefix=settings.api_v1_prefix)

    error_statuses: dict[type[DomainError], int] = {
        NotFoundError: status.HTTP_404_NOT_FOUND,
        ConflictError: status.HTTP_409_CONFLICT,
        AuthenticationError: status.HTTP_401_UNAUTHORIZED,
        RefreshTokenReuseError: status.HTTP_401_UNAUTHORIZED,
        PermissionDeniedError: status.HTTP_403_FORBIDDEN,
        ValidationError: status.HTTP_422_UNPROCESSABLE_CONTENT,
        ServiceUnavailableError: status.HTTP_503_SERVICE_UNAVAILABLE,
    }

    @application.exception_handler(DomainError)
    async def domain_error_handler(_: Request, error: DomainError) -> JSONResponse:
        status_code = next(
            (
                error_status
                for error_type, error_status in error_statuses.items()
                if isinstance(error, error_type)
            ),
            status.HTTP_400_BAD_REQUEST,
        )
        return JSONResponse(
            status_code=status_code,
            content={"detail": str(error)},
            headers={"WWW-Authenticate": "Bearer"}
            if isinstance(error, AuthenticationError)
            else None,
        )

    @application.exception_handler(IntegrityError)
    async def integrity_error_handler(_: Request, __: IntegrityError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Конфликт целостности данных"},
        )

    return application


app = create_app()
