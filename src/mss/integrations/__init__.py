"""Device integrations.

Every integration must:

- Use an official vendor API or a documented service interface.
- Accept an ``AuthorizationRecord`` for any mutating action.
- Refuse to act when the record does not match the target device.
- Never implement activation-lock, FRP, carrier-lock, or screen-lock bypass.
"""

from mss.integrations.android import AdbError, AdbService, AndroidDevice

__all__ = [
    "AdbError",
    "AdbService",
    "AndroidDevice",
]