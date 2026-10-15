from __future__ import annotations

from dataclasses import dataclass

from mss.core.authorization import AuthorizationRecord


class AppleServiceError(Exception):
    pass


@dataclass
class AppleDevice:
    udid: str
    name: str | None = None


class AppleService:
    """Placeholder for Apple Configurator / MDM authorized workflows.

    Only Apple-approved MDM/DEP/ADE flows and owner-authorized restores belong here.
    No Activation Lock bypass. No iCloud bypass.
    """

    def list_devices(self) -> list[AppleDevice]:
        raise NotImplementedError(
            "Integrate with Apple Configurator CLI or MDM API for authorized devices."
        )

    def restore(self, udid: str, authorization: AuthorizationRecord) -> None:
        if authorization.device_id != udid:
            raise AppleServiceError("Authorization device mismatch")
        raise NotImplementedError(
            "Use Apple Configurator restore for owner-authorized devices only."
        )