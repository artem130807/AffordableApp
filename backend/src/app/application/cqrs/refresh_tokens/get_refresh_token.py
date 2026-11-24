from dataclasses import dataclass

from app.application.ports.security import TokenServicePort
from app.domain.entities import RefreshToken
from app.domain.repositories import RefreshTokenRepository


@dataclass(frozen=True, slots=True)
class GetRefreshTokenQuery:
    raw_token: str


class GetRefreshTokenHandler:
    def __init__(
        self,
        tokens: RefreshTokenRepository,
        token_service: TokenServicePort,
    ) -> None:
        self.tokens = tokens
        self.token_service = token_service

    async def handle(self, query: GetRefreshTokenQuery) -> RefreshToken | None:
        return await self.tokens.get_by_hash(self.token_service.hash_refresh_token(query.raw_token))
