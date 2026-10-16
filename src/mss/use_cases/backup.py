from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mss.core.audit import AuditLog
from mss.core.authorization import AuthorizationError, AuthorizationGate
from mss.core.rbac import Permission, Principal
from mss.core.store import AuthorizationStore
from mss.integrations.android import AdbService


@dataclass
class BackupRequest:
    device_id: str
    out_path: Path


class BackupAndroidDevice:
    def __init__(
        self,
        store: AuthorizationStore,
        audit: AuditLog,
        adb: AdbService,
    ):
        self.store = store
        self.audit = audit
        self.adb = adb

    def run(self, principal: Principal, req: BackupRequest) -> Path:
        principal.require(Permission.BACKUP_DEVICE)

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
                }
            )
            raise

        self.audit.append(
            {
                "event": "device_backup_started",
                "device_id": req.device_id,
                "operator": principal.user_id,
                "out_path": str(req.out_path),
            }
        )

        self.adb.backup(req.device_id, authorization, str(req.out_path))

        self.audit.append(
            {
                "event": "device_backup_completed",
                "device_id": req.device_id,
                "operator": principal.user_id,
                "out_path": str(req.out_path),
            }
        )
        return req.out_path