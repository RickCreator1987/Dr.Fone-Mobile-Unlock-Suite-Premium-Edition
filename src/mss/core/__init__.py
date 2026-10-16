"""Core compliance primitives.

These modules contain no device-specific logic. They are safe to unit test
without any hardware or OEM tooling present.
"""

from mss.core.audit import AuditLog
from mss.core.authorization import (
    AuthorizationError,
    AuthorizationGate,
    AuthorizationRecord,
    ConsentType,
)
from mss.core.rbac import (
    Permission,
    PermissionError_,
    Principal,
    Role,
)
from mss.core.store import AuthorizationStore

__all__ = [
    "AuditLog",
    "AuthorizationError",
    "AuthorizationGate",
    "AuthorizationRecord",
    "ConsentType",
    "Permission",
    "PermissionError_",
    "Principal",
    "Role",
    "AuthorizationStore",
]