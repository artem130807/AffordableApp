from dataclasses import dataclass

from app.application.ports.security import TokenServicePort
from app.domain.repositories import RefreshTokenRepository


@dataclass(frozen=True, slots=True)
class RevokeRefreshTokenCommand:
    raw_token: str


class RevokeRefreshTokenHandler:
    def __init__(
        self,
        tokens: RefreshTokenRepository,
        token_service: TokenServicePort,
    ) -> None:
        self.tokens = tokens
        self.token_service = token_service

    async def handle(self, command: RevokeRefreshTokenCommand) -> None:
        token = await self.tokens.get_by_hash(
            self.token_service.hash_refresh_token(command.raw_token),
            for_update=True,
        )
        if token and token.is_active:
            token.revoke()
            await self.tokens.update(token)
