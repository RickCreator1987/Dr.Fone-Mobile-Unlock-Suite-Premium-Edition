from __future__ import annotations

import subprocess
from dataclasses import dataclass

from mss.core.authorization import AuthorizationRecord


class AdbError(Exception):
    pass


@dataclass
class AndroidDevice:
    serial: str


class AdbService:
    """Wraps adb. Only read-only or owner-authorized operations allowed."""

    def __init__(self, adb_path: str = "adb"):
        self.adb_path = adb_path

    def _run(self, *args: str) -> str:
        try:
            result = subprocess.run(
                [self.adb_path, *args],
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )
        except FileNotFoundError as exc:
            raise AdbError("adb not found") from exc
        except subprocess.CalledProcessError as exc:
            raise AdbError(exc.stderr.strip()) from exc
        return result.stdout

    def list_devices(self) -> list[AndroidDevice]:
        out = self._run("devices")
        devices = []
        for line in out.splitlines()[1:]:
            line = line.strip()
            if not line:
                continue
            serial, _, state = line.partition("\t")
            if state.strip() == "device":
                devices.append(AndroidDevice(serial=serial))
        return devices

    def get_props(self, serial: str) -> dict[str, str]:
        out = self._run("-s", serial, "shell", "getprop")
        props: dict[str, str] = {}
        for line in out.splitlines():
            if "]: [" in line:
                key, _, rest = line.partition("]: [")
                key = key.lstrip("[").strip()
                value = rest.rstrip("]").strip()
                props[key] = value
        return props

    def backup(self, serial: str, authorization: AuthorizationRecord, out_path: str) -> None:
        if authorization.device_id != serial:
            raise AdbError("Authorization device mismatch")
        # Owner-authorized backup only. Uses documented adb backup interface.
        self._run("-s", serial, "backup", "-apk", "-shared", "-all", "-f", out_path)