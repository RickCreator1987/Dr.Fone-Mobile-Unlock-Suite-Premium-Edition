from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from mss.core.audit import AuditLog
from mss.core.authorization import AuthorizationError, ConsentType
from mss.core.rbac import PermissionError_, Principal, Role
from mss.core.store import AuthorizationStore
from mss.use_cases.authorize import AuthorizeDevice, AuthorizeRequest


def _evidence(tmp_path: Path) -> Path:
    p = tmp_path / "consent.pdf"
    p.write_text("signed consent", encoding="utf-8")
    return p


def test_authorize_requires_reviewer_or_admin(tmp_path: Path) -> None:
    store = AuthorizationStore(tmp_path / "mss.db")
    audit = AuditLog(tmp_path / "audit.jsonl")
    use_case = AuthorizeDevice(store=store, audit=audit)
    tech = Principal(user_id="t", roles=frozenset({Role.TECHNICIAN}))

    with pytest.raises(PermissionError_):
        use_case.run(
            tech,
            AuthorizeRequest(
                device_id="dev-1",
                consent_type=ConsentType.OWNER,
                authorized_by="owner@example.com",
                evidence_path=_evidence(tmp_path),
            ),
        )


def test_authorize_happy_path(tmp_path: Path) -> None:
    store = AuthorizationStore(tmp_path / "mss.db")
    audit = AuditLog(tmp_path / "audit.jsonl")
    use_case = AuthorizeDevice(store=store, audit=audit, signing_key=b"k" * 32)
    reviewer = Principal(user_id="r", roles=frozenset({Role.REVIEWER}))

    result = use_case.run(
        reviewer,
        AuthorizeRequest(
            device_id="dev-1",
            consent_type=ConsentType.OWNER,
            authorized_by="owner@example.com",
            evidence_path=_evidence(tmp_path),
        ),
    )

    assert result.authorization_id >= 1
    assert len(result.evidence_sha256) == 64
    assert result.signature is not None
    assert audit.verify() is True
    assert len(store.active_for("dev-1")) == 1


def test_authorize_rejects_expired(tmp_path: Path) -> None:
    store = AuthorizationStore(tmp_path / "mss.db")
    audit = AuditLog(tmp_path / "audit.jsonl")
    use_case = AuthorizeDevice(store=store, audit=audit)
    reviewer = Principal(user_id="r", roles=frozenset({Role.REVIEWER}))

    with pytest.raises(AuthorizationError):
        use_case.run(
            reviewer,
            AuthorizeRequest(
                device_id="dev-1",
                consent_type=ConsentType.OWNER,
                authorized_by="owner@example.com",
                evidence_path=_evidence(tmp_path),
                expires_at=datetime.now(timezone.utc) - timedelta(days=1),
            ),
        )