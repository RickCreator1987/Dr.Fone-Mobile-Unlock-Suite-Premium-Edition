from __future__ import annotations

from typing import Protocol

from mss.core.authorization import AuthorizationRecord


class DeviceService(Protocol):
    """Only official, authorized OEM/service operations belong here."""

    def read_info(self, device_id: str) -> dict:
        ...

    def backup(self, device_id: str, authorization: AuthorizationRecord) -> str:
        ...

    def factory_reset(self, device_id: str, authorization: AuthorizationRecord) -> None:
        ...