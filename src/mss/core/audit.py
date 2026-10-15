from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GENESIS = "0" * 64


class AuditLog:
    """Append-only, tamper-evident JSONL audit log."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.touch()

    def _last_hash(self) -> str:
        last = GENESIS
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    last = json.loads(line)["hash"]
        return last

    def append(self, event: dict[str, Any]) -> dict[str, Any]:
        prev = self._last_hash()
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            **event,
            "prev_hash": prev,
        }
        payload = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
        record["hash"] = hashlib.sha256(payload).hexdigest()

        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, sort_keys=True) + "\n")
        return record

    def verify(self) -> bool:
        prev = GENESIS
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                claimed = record.pop("hash")
                if record.get("prev_hash") != prev:
                    return False
                payload = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
                if hashlib.sha256(payload).hexdigest() != claimed:
                    return False
                prev = claimed
        return True