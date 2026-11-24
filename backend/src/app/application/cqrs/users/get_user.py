from dataclasses import dataclass
from uuid import UUID

from app.domain.entities import User
from app.domain.exceptions import NotFoundError
from app.domain.repositories import UserRepository


@dataclass(frozen=True, slots=True)
class GetUserQuery:
    user_id: UUID


class GetUserHandler:
    def __init__(self, users: UserRepository) -> None:
        self.users = users

    async def handle(self, query: GetUserQuery) -> User:
        user = await self.users.get(query.user_id)
        if user is None:
            raise NotFoundError("Пользователь не найден")
        return user
