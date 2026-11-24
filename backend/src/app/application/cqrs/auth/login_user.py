from dataclasses import dataclass

from app.application.cqrs.auth.token_pair import TokenPair
from app.application.cqrs.refresh_tokens import (
    IssueRefreshTokenCommand,
    IssueRefreshTokenHandler,
)
from app.application.ports.security import PasswordHasherPort, TokenServicePort
from app.domain.entities import User
from app.domain.exceptions import AuthenticationError
from app.domain.repositories import UserRepository


@dataclass(frozen=True, slots=True)
class LoginUserCommand:
    email: str
    password: str
    user_agent: str | None = None
    ip_address: str | None = None


class LoginUserHandler:
    def __init__(
        self,
        users: UserRepository,
        password_hasher: PasswordHasherPort,
        token_service: TokenServicePort,
        issue_refresh_token: IssueRefreshTokenHandler,
    ) -> None:
        self.users = users
        self.password_hasher = password_hasher
        self.token_service = token_service
        self.issue_refresh_token = issue_refresh_token

    def _create_access_token(self, user: User) -> str:
        return self.token_service.create_access_token(
            user_id=user.id,
            roles=[role.name for role in user.roles],
            permissions=user.permissions,
        )

    async def handle(self, command: LoginUserCommand) -> TokenPair:
        user = await self.users.get_by_email(command.email)
        password_is_valid = self.password_hasher.verify(
            command.password,
            user.password_hash if user else None,
        )
        if user is None or not user.is_active or not password_is_valid:
            raise AuthenticationError("Неверный email или пароль")
        refresh = await self.issue_refresh_token.handle(
            IssueRefreshTokenCommand(
                user=user,
                user_agent=command.user_agent,
                ip_address=command.ip_address,
            )
        )
        return TokenPair(
            access_token=self._create_access_token(user),
            refresh_token=refresh.raw_token,
        )
