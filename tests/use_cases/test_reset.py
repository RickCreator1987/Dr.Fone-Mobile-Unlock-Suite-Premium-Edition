from datetime import datetime, timezone
from pathlib import Path

import pytest

from mss.core.audit import AuditLog
from mss.core.authorization import (
    AuthorizationRecord,
    ConsentType,
)
from mss.core.rbac import PermissionError_, Principal, Role
from mss.core.store import AuthorizationStore
from mss.use_cases.reset import FactoryResetAndroidDevice, ResetRequest


class FakeAdb:
    def __init__(self):
        self.calls: list[tuple] = []

    def _run(self, *args: str) -> str:
        self.calls.append(args)
        return ""


def test_reset_requires_confirmation(tmp_path: Path) -> None:
    store = AuthorizationStore(tmp_path / "mss.db")
    audit = AuditLog(tmp_path / "audit.jsonl")
    use_case = FactoryResetAndroidDevice(store=store, audit=audit, adb=FakeAdb())
    admin = Principal(user_id="a", roles=frozenset({Role.ADMIN}))

    with pytest.raises(ValueError):
        use_case.run(admin, ResetRequest(device_id="dev-1", confirm=False))


def test_reset_requires_admin(tmp_path: Path) -> None:
    store = AuthorizationStore(tmp_path / "mss.db")
    audit = AuditLog(tmp_path / "audit.jsonl")
    use_case = FactoryResetAndroidDevice(store=store, audit=audit, adb=FakeAdb())
    tech = Principal(user_id="t", roles=frozenset({Role.TECHNICIAN}))

    with pytest.raises(PermissionError_):
        use_case.run(tech, ResetRequest(device_id="dev-1", confirm=True))


def test_reset_happy_path(tmp_path: Path) -> None:
    store = AuthorizationStore(tmp_path / "mss.db")
    audit = AuditLog(tmp_path / "audit.jsonl")
    adb = FakeAdb()

    evidence = tmp_path / "consent.pdf"
    evidence.write_text("signed", encoding="utf-8")

    store.add(
        AuthorizationRecord(
            device_id="dev-1",
            consent_type=ConsentType.OWNER,
            authorized_by="owner@example.com",
            timestamp=datetime.now(timezone.utc),
            evidence_path=evidence,
        )
    )

    admin = Principal(user_id="a", roles=frozenset({Role.ADMIN}))
    use_case = FactoryResetAndroidDevice(store=store, audit=audit, adb=adb)

    use_case.run(admin, ResetRequest(device_id="dev-1", confirm=True))

    assert adb.calls == [("-s", "dev-1", "reboot", "recovery")]
    assert audit.verify() is True