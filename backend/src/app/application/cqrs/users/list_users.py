from dataclasses import dataclass

from app.domain.entities import User
from app.domain.exceptions import ValidationError
from app.domain.repositories import UserRepository


@dataclass(frozen=True, slots=True)
class ListUsersQuery:
    offset: int = 0
    limit: int = 100


class ListUsersHandler:
    def __init__(self, users: UserRepository) -> None:
        self.users = users

    async def handle(self, query: ListUsersQuery) -> list[User]:
        if query.offset < 0 or not 1 <= query.limit <= 100:
            raise ValidationError("Некорректные параметры пагинации")
        return list(await self.users.list(offset=query.offset, limit=query.limit))
