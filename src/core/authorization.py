# src/core/authorization.py
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

class AuthorizationError(Exception):
    pass

class ConsentType(Enum):
    OWNER = "owner"
    SERVICE_PROVIDER = "service_provider"
    ENTERPRISE_ADMIN = "enterprise_admin"

@dataclass(frozen=True)
class AuthorizationRecord:
    device_id: str
    consent_type: ConsentType
    authorized_by: str
    timestamp: datetime
    evidence_path: Path
    expires_at: datetime | None = None

class AuthorizationGate:
    def __init__(self, records: list[AuthorizationRecord]):
        self._records = records

    def require(self, device_id: str) -> AuthorizationRecord:
        for record in self._records:
            if record.device_id != device_id:
                continue
            if record.expires_at and record.expires_at < datetime.utcnow():
                continue
            if not record.evidence_path.exists():
                continue
            return record
        raise AuthorizationError(f"No valid authorization for device {device_id}")
