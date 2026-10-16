from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from mss.integrations.android import AdbError, AdbService


FAKE_ADB = """#!/usr/bin/env bash
set -euo pipefail

if [ "$1" = "devices" ]; then
  cat <<EOF
List of devices attached
emulator-5554\tdevice
ABCD1234\tunauthorized
EOF
  exit 0
fi

if [ "$1" = "-s" ] && [ "$3" = "shell" ] && [ "$4" = "getprop" ]; then
  cat <<EOF
[ro.product.model]: [Pixel 7]
[ro.build.version.release]: [14]
EOF
  exit 0
fi

if [ "$1" = "-s" ] && [ "$3" = "backup" ]; then
  echo "backup done"
  exit 0
fi

echo "unsupported: $*" >&2
exit 1
"""


@pytest.fixture
def fake_adb(tmp_path: Path) -> Path:
    path = tmp_path / "adb"
    path.write_text(FAKE_ADB, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)
    return path


def test_list_devices(fake_adb: Path) -> None:
    svc = AdbService(str(fake_adb))
    devices = svc.list_devices()
    assert [d.serial for d in devices] == ["emulator-5554"]


def test_get_props(fake_adb: Path) -> None:
    svc = AdbService(str(fake_adb))
    props = svc.get_props("emulator-5554")
    assert props["ro.product.model"] == "Pixel 7"
    assert props["ro.build.version.release"] == "14"


def test_backup_device_mismatch(fake_adb: Path) -> None:
    from datetime import datetime, timezone

    from mss.core.authorization import AuthorizationRecord, ConsentType

    svc = AdbService(str(fake_adb))
    record = AuthorizationRecord(
        device_id="OTHER",
        consent_type=ConsentType.OWNER,
        authorized_by="owner@example.com",
        timestamp=datetime.now(timezone.utc),
        evidence_path=Path("/tmp/whatever"),
    )
    with pytest.raises(AdbError):
        svc.backup("emulator-5554", record, "/tmp/out.ab")


def test_backup_ok(fake_adb: Path, tmp_path: Path) -> None:
    from datetime import datetime, timezone

    from mss.core.authorization import AuthorizationRecord, ConsentType

    evidence = tmp_path / "consent.pdf"
    evidence.write_text("signed", encoding="utf-8")

    svc = AdbService(str(fake_adb))
    record = AuthorizationRecord(
        device_id="emulator-5554",
        consent_type=ConsentType.OWNER,
        authorized_by="owner@example.com",
        timestamp=datetime.now(timezone.utc),
        evidence_path=evidence,
    )
    svc.backup("emulator-5554", record, str(tmp_path / "out.ab"))