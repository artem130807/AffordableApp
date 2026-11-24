from enum import StrEnum


class PermissionCode(StrEnum):
    USERS_READ = "users:read"
    USERS_MANAGE = "users:manage"
    ROLES_MANAGE = "roles:manage"
    ORGANIZATIONS_READ = "organizations:read"
    ORGANIZATIONS_MANAGE = "organizations:manage"
    ORGANIZATIONS_ADMIN = "organizations:admin"
    CATALOGS_MANAGE = "catalogs:manage"
    ITEMS_MANAGE = "items:manage"


DEFAULT_USER_PERMISSIONS = frozenset(
    {
        PermissionCode.ORGANIZATIONS_READ.value,
        PermissionCode.ORGANIZATIONS_MANAGE.value,
        PermissionCode.CATALOGS_MANAGE.value,
        PermissionCode.ITEMS_MANAGE.value,
    }
)
ADMIN_PERMISSIONS = frozenset(permission.value for permission in PermissionCode)

SYSTEM_PERMISSION_NAMES: dict[PermissionCode, str] = {
    PermissionCode.USERS_READ: "Просмотр пользователей",
    PermissionCode.USERS_MANAGE: "Управление пользователями",
    PermissionCode.ROLES_MANAGE: "Управление ролями и правами",
    PermissionCode.ORGANIZATIONS_READ: "Просмотр организаций",
    PermissionCode.ORGANIZATIONS_MANAGE: "Управление организациями",
    PermissionCode.ORGANIZATIONS_ADMIN: "Управление всеми организациями",
    PermissionCode.CATALOGS_MANAGE: "Управление каталогами",
    PermissionCode.ITEMS_MANAGE: "Управление позициями каталога",
}
