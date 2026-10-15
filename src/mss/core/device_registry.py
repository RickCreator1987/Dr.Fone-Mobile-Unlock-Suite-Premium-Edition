from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Device:
    device_id: str
    platform: str
    owner: str
    notes: str = ""


class DeviceRegistry:
    def __init__(self, path: Path):
        self.path = Path(path)
        self._devices: dict[str, Device] = {}
        if self.path.exists():
            self._load()

    def _load(self) -> None:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        for item in data.get("devices", []):
            device = Device(**item)
            self._devices[device.device_id] = device

    def get(self, device_id: str) -> Device | None:
        return self._devices.get(device_id)

    def add(self, device: Device) -> None:
        self._devices[device.device_id] = device