from dataclasses import dataclass
from datetime import UTC, datetime

from app.application.ports.security import TokenServicePort
from app.domain.entities import RefreshToken, User
from app.domain.repositories import RefreshTokenRepository


@dataclass(frozen=True, slots=True)
class IssueRefreshTokenCommand:
    user: User
    user_agent: str | None = None
    ip_address: str | None = None


@dataclass(frozen=True, slots=True)
class IssuedRefreshToken:
    raw_token: str
    entity: RefreshToken


class IssueRefreshTokenHandler:
    def __init__(
        self,
        tokens: RefreshTokenRepository,
        token_service: TokenServicePort,
    ) -> None:
        self.tokens = tokens
        self.token_service = token_service

    async def handle(self, command: IssueRefreshTokenCommand) -> IssuedRefreshToken:
        raw_token, token_hash = self.token_service.create_refresh_token()
        entity = await self.tokens.add(
            RefreshToken(
                user_id=command.user.id,
                token_hash=token_hash,
                expires_at=datetime.now(UTC) + self.token_service.refresh_ttl,
                user_agent=command.user_agent,
                ip_address=command.ip_address,
            )
        )
        return IssuedRefreshToken(raw_token=raw_token, entity=entity)
