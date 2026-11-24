from dataclasses import dataclass

from app.application.ports.security import PasswordHasherPort
from app.domain.entities import User
from app.domain.exceptions import ConflictError, NotFoundError, ValidationError
from app.domain.repositories import RoleRepository, UserRepository
from app.domain.validation import normalize_email, normalize_required_text


@dataclass(frozen=True, slots=True)
class CreateUserCommand:
    email: str
    name: str
    password: str


class CreateUserHandler:
    def __init__(
        self,
        users: UserRepository,
        roles: RoleRepository,
        password_hasher: PasswordHasherPort,
    ) -> None:
        self.users = users
        self.roles = roles
        self.password_hasher = password_hasher

    async def handle(self, command: CreateUserCommand) -> User:
        email = normalize_email(command.email)
        name = normalize_required_text(
            command.name,
            field_name="Имя",
            min_length=2,
            max_length=120,
        )
        if await self.users.get_by_email(email):
            raise ConflictError("Пользователь с таким email уже существует")
        role = await self.roles.get_by_name("user")
        if role is None:
            raise NotFoundError("Базовая роль user не настроена")
        try:
            password_hash = self.password_hasher.hash(command.password)
        except ValueError as error:
            raise ValidationError(str(error)) from error
        return await self.users.add(
            User(email=email, name=name, password_hash=password_hash, roles=[role])
        )
