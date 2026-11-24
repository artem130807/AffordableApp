from dataclasses import dataclass
from uuid import UUID

from app.domain.entities import Permission
from app.domain.exceptions import NotFoundError
from app.domain.repositories import PermissionRepository


@dataclass(frozen=True, slots=True)
class GetPermissionQuery:
    permission_id: UUID


class GetPermissionHandler:
    def __init__(self, permissions: PermissionRepository) -> None:
        self.permissions = permissions

    async def handle(self, query: GetPermissionQuery) -> Permission:
        permission = await self.permissions.get(query.permission_id)
        if permission is None:
            raise NotFoundError("Право не найдено")
        return permission
