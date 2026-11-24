from app.domain.entities import Permission
from app.domain.repositories import PermissionRepository


class ListPermissionsHandler:
    def __init__(self, permissions: PermissionRepository) -> None:
        self.permissions = permissions

    async def handle(self) -> list[Permission]:
        return list(await self.permissions.list())
