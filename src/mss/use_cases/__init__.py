"""Use-case layer.

Each use case is a small orchestrator that:

1. Enforces RBAC on the calling principal.
2. Requires a valid ``AuthorizationRecord`` for the target device.
3. Calls an integration (adb, Configurator, MDM) via an official interface.
4. Writes a tamper-evident entry to the ``AuditLog``.

No use case in this package may bypass OEM security (iCloud Activation Lock,
Google FRP, carrier locks, screen locks, or encryption).
"""

from mss.use_cases.authorize import (
    AuthorizeDevice,
    AuthorizeRequest,
    AuthorizeResult,
)
from mss.use_cases.backup import BackupAndroidDevice, BackupRequest

__all__ = [
    "AuthorizeDevice",
    "AuthorizeRequest",
    "AuthorizeResult",
    "BackupAndroidDevice",
    "BackupRequest",
]