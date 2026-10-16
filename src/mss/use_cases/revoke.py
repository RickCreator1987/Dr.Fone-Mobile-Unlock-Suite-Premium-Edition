"""Revocation use case.

Revokes a previously granted authorization. Always audited.
"""

from __future__ import annotations

from dataclasses import dataclass

from mss.core.audit import AuditLog
from mss.core.rbac import Permission, Principal
from mss.core.store import AuthorizationStore


@dataclass
class RevokeRequest:
    authorization_id: int
    reason: str


class RevokeAuthorization:
    def __init__(self, store: AuthorizationStore, audit: AuditLog):
        self.store = store
        self.audit = audit

    def run(self, principal: Principal, req: RevokeRequest) -> None:
        principal.require(Permission.APPROVE_AUTHORIZATION)

        self.store.revoke(req.authorization_id)

        self.audit.append(
            {
                "event": "authorization_revoked",
                "authorization_id": req.authorization_id,
                "operator": principal.user_id,
                "reason": req.reason,
            }
        )