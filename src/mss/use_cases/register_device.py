"""Device onboarding use case.

Registers a device in the local registry. Does not modify the device.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from mss.core.audit import AuditLog
from mss.core.device_registry import Device
from mss.core.rbac import Permission, Principal


@dataclass
class RegisterDeviceRequest:
    device_id: str
    platform: str
    owner: str
    notes: str = ""


class RegisterDevice:
    def __init__(self, registry, audit: AuditLog):
        self.registry = registry
        self.audit = audit

    def run(self, principal: Principal, req: RegisterDeviceRequest) -> Device:
        principal.require(Permission.MANAGE_USERS)

        device = Device(
            device_id=req.device_id,
            platform=req.platform,
            owner=req.owner,
            notes=req.notes,
        )
        self.registry.add(device)

        self.audit.append(
            {
                "event": "device_registered",
                "device_id": req.device_id,
                "platform": req.platform,
                "operator": principal.user_id,
                "ts_action": datetime.now(timezone.utc).isoformat(),
            }
        )
        return device