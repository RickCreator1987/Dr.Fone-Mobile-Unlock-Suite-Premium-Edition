from datetime import datetime, timezone
from pathlib import Path

import pytest

from mss.core.audit import AuditLog
from mss.core.authorization import (
    AuthorizationError,
    AuthorizationRecord,
    ConsentType,
)
from mss.core.rbac import PermissionError_, Principal, Role
from mss.core.store import AuthorizationStore
from mss.use_cases.backup import BackupAndroidDevice, BackupRequest


class FakeAdb:
    def __init__(self):
        self.calls: list[tuple] = []

    def backup(self, device_id: str, authorization, out_path: str) -> None:
        self.calls.append(("backup", device_id, out_path))


@pytest.fixture
def store(tmp_path: Path) -> AuthorizationStore:
    return AuthorizationStore(tmp_path / "mss.db")


def _evidence(tmp_path: Path) -> Path:
    p = tmp_path / "consent.pdf"
    p.write_text("signed", encoding="utf-8")
    return p


def test_backup_requires_permission(tmp_path: Path, store: AuthorizationStore) -> None:
    audit = AuditLog(tmp_path / "audit.jsonl")
    use_case = BackupAndroidDevice(store=store, audit=audit, adb=FakeAdb())
    viewer = Principal(user_id="v", roles=frozenset({Role.VIEWER}))

    with pytest.raises(PermissionError_):
        use_case.run(viewer, BackupRequest(device_id="dev-1", out_path=tmp_path / "out"))


def test_backup_denied_without_authorization(tmp_path: Path, store: AuthorizationStore) -> None:
    audit = AuditLog(tmp_path / "audit.jsonl")
    use_case = BackupAndroidDevice(store=store, audit=audit, adb=FakeAdb())
    tech = Principal(user_id="t", roles=frozenset({Role.TECHNICIAN}))

    with pytest.raises(AuthorizationError):
        use_case.run(tech, BackupRequest(device_id="dev-1", out_path=tmp_path / "out"))

    lines = (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()
    assert any('"authorization_denied"' in line for line in lines)


def test_backup_succeeds_with_authorization(tmp_path: Path, store: AuthorizationStore) -> None:
    audit = AuditLog(tmp_path / "audit.jsonl")
    adb = FakeAdb()

    evidence = _evidence(tmp_path)
    record = AuthorizationRecord(
        device_id="dev-1",
        consent_type=ConsentType.OWNER,
        authorized_by="owner@example.com",
        timestamp=datetime.now(timezone.utc),
        evidence_path=evidence,
    )
    store.add(record)

    tech = Principal(user_id="t", roles=frozenset({Role.TECHNICIAN}))
    use_case = BackupAndroidDevice(store=store, audit=audit, adb=adb)
    out = tmp_path / "backup.ab"

    result = use_case.run(tech, BackupRequest(device_id="dev-1", out_path=out))

    assert result == out
    assert adb.calls == [("backup", "dev-1", str(out))]
    assert audit.verify() is True