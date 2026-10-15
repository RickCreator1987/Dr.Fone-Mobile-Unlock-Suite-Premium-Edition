from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Iterable


class AuthorizationError(Exception):
    """Raised when no valid authorization exists for a device action."""


class ConsentType(str, Enum):
    OWNER = "owner"
    SERVICE_PROVIDER = "service_provider"
    ENTERPRISE_ADMIN = "enterprise_admin"
    LEGAL_REQUEST = "legal_request"


@dataclass(frozen=True)
class AuthorizationRecord:
    device_id: str
    consent_type: ConsentType
    authorized_by: str
    timestamp: datetime
    evidence_path: Path
    expires_at: datetime | None = None

    def is_valid(self, now: datetime | None = None) -> bool:
        now = now or datetime.now(timezone.utc)
        if self.expires_at and self.expires_at <= now:
            return False
        if not self.evidence_path.exists():
            return False
        return True


class AuthorizationGate:
    def __init__(self, records: Iterable[AuthorizationRecord] = ()):
        self._records = list(records)

    def add(self, record: AuthorizationRecord) -> None:
        self._records.append(record)

    def require(self, device_id: str, now: datetime | None = None) -> AuthorizationRecord:
        for record in self._records:
            if record.device_id == device_id and record.is_valid(now):
                return record
        raise AuthorizationError(f"No valid authorization for device {device_id}")