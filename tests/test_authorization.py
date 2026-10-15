from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from mss.core.authorization import (
    AuthorizationError,
    AuthorizationGate,
    AuthorizationRecord,
    ConsentType,
)


def test_valid_authorization(tmp_path: Path) -> None:
    evidence = tmp_path / "consent.pdf"
    evidence.write_text("signed consent", encoding="utf-8")

    record = AuthorizationRecord(
        device_id="dev-1",
        consent_type=ConsentType.OWNER,
        authorized_by="owner@example.com",
        timestamp=datetime.now(timezone.utc),
        evidence_path=evidence,
    )

    gate = AuthorizationGate([record])
    assert gate.require("dev-1") == record


def test_missing_evidence_denied(tmp_path: Path) -> None:
    record = AuthorizationRecord(
        device_id="dev-1",
        consent_type=ConsentType.OWNER,
        authorized_by="owner@example.com",
        timestamp=datetime.now(timezone.utc),
        evidence_path=tmp_path / "missing.pdf",
    )

    gate = AuthorizationGate([record])
    with pytest.raises(AuthorizationError):
        gate.require("dev-1")


def test_expired_authorization_denied(tmp_path: Path) -> None:
    evidence = tmp_path / "consent.pdf"
    evidence.write_text("signed consent", encoding="utf-8")

    record = AuthorizationRecord(
        device_id="dev-1",
        consent_type=ConsentType.OWNER,
        authorized_by="owner@example.com",
        timestamp=datetime.now(timezone.utc),
        evidence_path=evidence,
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
    )

    gate = AuthorizationGate([record])
    with pytest.raises(AuthorizationError):
        gate.require("dev-1")