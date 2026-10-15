# src/core/audit.py
import json
from datetime import datetime
from pathlib import Path

class AuditLog:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: dict):
        event = {"ts": datetime.utcnow().isoformat(), **event}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, sort_keys=True) + "\n")
