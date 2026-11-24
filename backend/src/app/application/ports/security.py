from datetime import timedelta
from typing import Protocol
from uuid import UUID


class PasswordHasherPort(Protocol):
    def hash(self, password: str) -> str: ...
    def verify(self, password: str, encoded: str | None) -> bool: ...


class TokenServicePort(Protocol):
    refresh_ttl: timedelta

    def create_access_token(
        self,
        *,
        user_id: UUID,
        roles: list[str],
        permissions: frozenset[str],
    ) -> str: ...

    def create_refresh_token(self) -> tuple[str, str]: ...
    def hash_refresh_token(self, raw_token: str) -> str: ...
