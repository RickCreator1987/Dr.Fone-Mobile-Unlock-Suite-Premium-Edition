from datetime import datetime, timedelta, timezone
from pathlib import Path

from mss.core.audit import AuditLog
from mss.core.authorization import AuthorizationRecord, ConsentType
from mss.core.retention import run_retention
from mss.core.store import AuthorizationStore


def test_retention_deletes_expired(tmp_path: Path) -> None:
    db = tmp_path / "mss.db"
    store = AuthorizationStore(db)
    audit = AuditLog(tmp_path / "audit.jsonl")

    evidence = tmp_path / "consent.pdf"
    evidence.write_text("signed", encoding="utf-8")

    store.add(
        AuthorizationRecord(
            device_id="dev-1",
            consent_type=ConsentType.OWNER,
            authorized_by="owner@example.com",
            timestamp=datetime.now(timezone.utc),
            evidence_path=evidence,
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        )
    )
    store.close()

    report = run_retention(db, audit)

    assert report.authorizations_deleted == 1
    assert report.evidence_deleted == 1
    assert not evidence.exists()
    assert audit.verify() is True