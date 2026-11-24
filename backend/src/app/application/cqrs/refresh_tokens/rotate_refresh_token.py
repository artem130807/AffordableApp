from dataclasses import dataclass

from app.application.cqrs.refresh_tokens.issue_refresh_token import (
    IssuedRefreshToken,
    IssueRefreshTokenCommand,
    IssueRefreshTokenHandler,
)
from app.application.ports.security import TokenServicePort
from app.domain.entities import User
from app.domain.exceptions import AuthenticationError, RefreshTokenReuseError
from app.domain.repositories import RefreshTokenRepository, UserRepository


@dataclass(frozen=True, slots=True)
class RotateRefreshTokenCommand:
    raw_token: str
    user_agent: str | None = None
    ip_address: str | None = None


class RotateRefreshTokenHandler:
    def __init__(
        self,
        tokens: RefreshTokenRepository,
        users: UserRepository,
        token_service: TokenServicePort,
    ) -> None:
        self.tokens = tokens
        self.users = users
        self.token_service = token_service
        self.issue_handler = IssueRefreshTokenHandler(tokens, token_service)

    async def handle(
        self,
        command: RotateRefreshTokenCommand,
    ) -> tuple[User, IssuedRefreshToken]:
        old = await self.tokens.get_by_hash(
            self.token_service.hash_refresh_token(command.raw_token),
            for_update=True,
        )
        if old is None:
            raise AuthenticationError("Refresh-токен недействителен или просрочен")
        if old.revoked_at is not None:
            await self.tokens.revoke_all_for_user(old.user_id)
            raise RefreshTokenReuseError(
                "Обнаружено повторное использование refresh-токена; все сессии отозваны"
            )
        if not old.is_active:
            raise AuthenticationError("Refresh-токен недействителен или просрочен")
        user = await self.users.get(old.user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("Пользователь не найден или заблокирован")
        issued = await self.issue_handler.handle(
            IssueRefreshTokenCommand(
                user=user,
                user_agent=command.user_agent,
                ip_address=command.ip_address,
            )
        )
        old.revoke(replaced_by_token_id=issued.entity.id)
        await self.tokens.update(old)
        return user, issued
