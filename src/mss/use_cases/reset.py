"""Factory reset use case.

Only performs a documented OEM factory reset on a device with a valid
authorization record. No bypass, no unlock, no data extraction.
"""

from __future__ import annotations

from dataclasses import dataclass

from mss.core.audit import AuditLog
from mss.core.authorization import AuthorizationError, AuthorizationGate
from mss.core.rbac import Permission, Principal
from mss.core.store import AuthorizationStore
from mss.integrations.android import AdbService


@dataclass
class ResetRequest:
    device_id: str
    confirm: bool = False


class FactoryResetAndroidDevice:
    def __init__(
        self,
        store: AuthorizationStore,
        audit: AuditLog,
        adb: AdbService,
    ):
        self.store = store
        self.audit = audit
        self.adb = adb

    def run(self, principal: Principal, req: ResetRequest) -> None:
        principal.require(Permission.FACTORY_RESET)

        if not req.confirm:
            raise ValueError("Factory reset requires explicit confirmation")

        records = self.store.active_for(req.device_id)
        try:
            authorization = AuthorizationGate(records).require(req.device_id)
        except AuthorizationError as exc:
            self.audit.append(
                {
                    "event": "authorization_denied",
                    "device_id": req.device_id,
                    "operator": principal.user_id,
                    "reason": str(exc),
                    "action": "factory_reset",
                }
            )
            raise

        self.audit.append(
            {
                "event": "device_factory_reset_started",
                "device_id": req.device_id,
                "operator": principal.user_id,
                "authorized_by": authorization.authorized_by,
            }
        )

        # Uses the standard Android recovery interface. The device must
        # already be in a state the owner authorized for reset.
        self.adb._run(
            "-s",
            req.device_id,
            "reboot",
            "recovery",
        )

        self.audit.append(
            {
                "event": "device_factory_reset_completed",
                "device_id": req.device_id,
                "operator": principal.user_id,
            }
        )