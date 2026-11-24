from fastapi import APIRouter, Request, status

from app.application.cqrs.auth import (
    LoginUserCommand,
    LoginUserHandler,
    RefreshSessionCommand,
    RefreshSessionHandler,
)
from app.application.cqrs.refresh_tokens import (
    IssueRefreshTokenHandler,
    RevokeRefreshTokenCommand,
    RevokeRefreshTokenHandler,
    RotateRefreshTokenHandler,
)
from app.application.cqrs.users import CreateUserCommand, CreateUserHandler
from app.application.ports import TokenServicePort
from app.presentation.api.dependencies import (
    CurrentUser,
    PasswordHasherDep,
    TokenServiceDep,
    UnitOfWorkDep,
)
from app.presentation.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth")


def _client_metadata(request: Request) -> tuple[str | None, str | None]:
    raw_user_agent = request.headers.get("user-agent")
    user_agent = raw_user_agent[:255] if raw_user_agent else None
    raw_ip_address = request.client.host if request.client else None
    ip_address = raw_ip_address[:64] if raw_ip_address else None
    return user_agent, ip_address


def _issue_refresh_handler(
    unit_of_work: UnitOfWorkDep,
    token_service: TokenServicePort,
) -> IssueRefreshTokenHandler:
    return IssueRefreshTokenHandler(
        unit_of_work.refresh_tokens,
        token_service,
    )


def _rotate_refresh_handler(
    unit_of_work: UnitOfWorkDep,
    token_service: TokenServicePort,
) -> RotateRefreshTokenHandler:
    return RotateRefreshTokenHandler(
        unit_of_work.refresh_tokens,
        unit_of_work.users,
        token_service,
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    unit_of_work: UnitOfWorkDep,
    password_hasher: PasswordHasherDep,
) -> UserResponse:
    handler = CreateUserHandler(
        unit_of_work.users,
        unit_of_work.roles,
        password_hasher,
    )
    user = await handler.handle(
        CreateUserCommand(
            email=str(payload.email),
            name=payload.name,
            password=payload.password.get_secret_value(),
        )
    )
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    unit_of_work: UnitOfWorkDep,
    token_service: TokenServiceDep,
    password_hasher: PasswordHasherDep,
) -> TokenResponse:
    user_agent, ip_address = _client_metadata(request)
    handler = LoginUserHandler(
        unit_of_work.users,
        password_hasher,
        token_service,
        _issue_refresh_handler(unit_of_work, token_service),
    )
    result = await handler.handle(
        LoginUserCommand(
            email=str(payload.email),
            password=payload.password.get_secret_value(),
            user_agent=user_agent,
            ip_address=ip_address,
        )
    )
    return TokenResponse.model_validate(result, from_attributes=True)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest,
    request: Request,
    unit_of_work: UnitOfWorkDep,
    token_service: TokenServiceDep,
) -> TokenResponse:
    user_agent, ip_address = _client_metadata(request)
    handler = RefreshSessionHandler(
        token_service,
        _rotate_refresh_handler(unit_of_work, token_service),
    )
    result = await handler.handle(
        RefreshSessionCommand(
            refresh_token=payload.refresh_token.get_secret_value(),
            user_agent=user_agent,
            ip_address=ip_address,
        )
    )
    return TokenResponse.model_validate(result, from_attributes=True)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    payload: RefreshRequest,
    unit_of_work: UnitOfWorkDep,
    token_service: TokenServiceDep,
) -> None:
    handler = RevokeRefreshTokenHandler(
        unit_of_work.refresh_tokens,
        token_service,
    )
    await handler.handle(
        RevokeRefreshTokenCommand(raw_token=payload.refresh_token.get_secret_value())
    )


@router.get("/me", response_model=UserResponse)
async def me(user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(user)
