from typing import Protocol
from uuid import UUID

from app.domain.entities import RefreshToken


class RefreshTokenRepository(Protocol):
    async def add(self, token: RefreshToken) -> RefreshToken: ...
    async def get_by_hash(
        self,
        token_hash: str,
        *,
        for_update: bool = False,
    ) -> RefreshToken | None: ...
    async def update(self, token: RefreshToken) -> RefreshToken: ...
    async def revoke_all_for_user(self, user_id: UUID) -> None: ...
