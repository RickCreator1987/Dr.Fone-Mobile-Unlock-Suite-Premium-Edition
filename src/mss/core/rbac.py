from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Role(str, Enum):
    VIEWER = "viewer"
    TECHNICIAN = "technician"
    REVIEWER = "reviewer"
    ADMIN = "admin"


class Permission(str, Enum):
    READ_DEVICE = "read_device"
    BACKUP_DEVICE = "backup_device"
    FACTORY_RESET = "factory_reset"
    APPROVE_AUTHORIZATION = "approve_authorization"
    EXPORT_AUDIT = "export_audit"
    MANAGE_USERS = "manage_users"


ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.VIEWER: {Permission.READ_DEVICE},
    Role.TECHNICIAN: {Permission.READ_DEVICE, Permission.BACKUP_DEVICE},
    Role.REVIEWER: {
        Permission.READ_DEVICE,
        Permission.APPROVE_AUTHORIZATION,
        Permission.EXPORT_AUDIT,
    },
    Role.ADMIN: set(Permission),
}


class PermissionError_(Exception):
    pass


@dataclass(frozen=True)
class Principal:
    user_id: str
    roles: frozenset[Role] = field(default_factory=frozenset)

    def permissions(self) -> set[Permission]:
        out: set[Permission] = set()
        for role in self.roles:
            out |= ROLE_PERMISSIONS.get(role, set())
        return out

    def require(self, permission: Permission) -> None:
        if permission not in self.permissions():
            raise PermissionError_(
                f"User {self.user_id} lacks permission {permission.value}"
            )