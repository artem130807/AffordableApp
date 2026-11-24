from dataclasses import dataclass

from app.application.cqrs.auth.token_pair import TokenPair
from app.application.cqrs.refresh_tokens import (
    RotateRefreshTokenCommand,
    RotateRefreshTokenHandler,
)
from app.application.ports.security import TokenServicePort
from app.domain.entities import User


@dataclass(frozen=True, slots=True)
class RefreshSessionCommand:
    refresh_token: str
    user_agent: str | None = None
    ip_address: str | None = None


class RefreshSessionHandler:
    def __init__(
        self,
        token_service: TokenServicePort,
        rotate_refresh_token: RotateRefreshTokenHandler,
    ) -> None:
        self.token_service = token_service
        self.rotate_refresh_token = rotate_refresh_token

    def _create_access_token(self, user: User) -> str:
        return self.token_service.create_access_token(
            user_id=user.id,
            roles=[role.name for role in user.roles],
            permissions=user.permissions,
        )

    async def handle(self, command: RefreshSessionCommand) -> TokenPair:
        user, refresh = await self.rotate_refresh_token.handle(
            RotateRefreshTokenCommand(
                raw_token=command.refresh_token,
                user_agent=command.user_agent,
                ip_address=command.ip_address,
            )
        )
        return TokenPair(
            access_token=self._create_access_token(user),
            refresh_token=refresh.raw_token,
        )
