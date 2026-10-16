from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from mss.core.audit import AuditLog
from mss.core.authorization import (
    AuthorizationError,
    AuthorizationGate,
    AuthorizationRecord,
    ConsentType,
)
from mss.core.consent import hash_file, sign_artifact
from mss.core.rbac import Permission, Principal
from mss.core.store import AuthorizationStore


@dataclass
class AuthorizeRequest:
    device_id: str
    consent_type: ConsentType
    authorized_by: str
    evidence_path: Path
    expires_at: datetime | None = None


@dataclass
class AuthorizeResult:
    authorization_id: int
    evidence_sha256: str
    signature: str | None


class AuthorizeDevice:
    def __init__(
        self,
        store: AuthorizationStore,
        audit: AuditLog,
        signing_key: bytes | None = None,
    ):
        self.store = store
        self.audit = audit
        self.signing_key = signing_key

    def run(self, principal: Principal, req: AuthorizeRequest) -> AuthorizeResult:
        principal.require(Permission.APPROVE_AUTHORIZATION)

        artifact = hash_file(req.evidence_path)
        signature = (
            sign_artifact(artifact, self.signing_key) if self.signing_key else None
        )

        record = AuthorizationRecord(
            device_id=req.device_id,
            consent_type=req.consent_type,
            authorized_by=req.authorized_by,
            timestamp=datetime.now(timezone.utc),
            evidence_path=req.evidence_path,
            expires_at=req.expires_at,
        )

        # Validate before persisting
        AuthorizationGate([record]).require(req.device_id)

        auth_id = self.store.add(record, evidence_sha256=artifact.sha256)

        self.audit.append(
            {
                "event": "authorization_granted",
                "authorization_id": auth_id,
                "device_id": req.device_id,
                "consent_type": req.consent_type.value,
                "authorized_by": req.authorized_by,
                "operator": principal.user_id,
                "evidence_sha256": artifact.sha256,
                "signature": signature,
            }
        )
        return AuthorizeResult(
            authorization_id=auth_id,
            evidence_sha256=artifact.sha256,
            signature=signature,
        )