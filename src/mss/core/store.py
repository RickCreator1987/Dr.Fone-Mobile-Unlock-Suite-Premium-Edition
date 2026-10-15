from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from mss.core.authorization import AuthorizationRecord, ConsentType


SCHEMA = """
CREATE TABLE IF NOT EXISTS authorizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    consent_type TEXT NOT NULL,
    authorized_by TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    evidence_path TEXT NOT NULL,
    evidence_sha256 TEXT,
    expires_at TEXT,
    revoked INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_auth_device ON authorizations(device_id);
"""


class AuthorizationStore:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    def add(
        self,
        record: AuthorizationRecord,
        evidence_sha256: str | None = None,
    ) -> int:
        cur = self._conn.execute(
            """
            INSERT INTO authorizations
              (device_id, consent_type, authorized_by, timestamp,
               evidence_path, evidence_sha256, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.device_id,
                record.consent_type.value,
                record.authorized_by,
                record.timestamp.isoformat(),
                str(record.evidence_path),
                evidence_sha256,
                record.expires_at.isoformat() if record.expires_at else None,
            ),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def revoke(self, authorization_id: int) -> None:
        self._conn.execute(
            "UPDATE authorizations SET revoked = 1 WHERE id = ?",
            (authorization_id,),
        )
        self._conn.commit()

    def active_for(self, device_id: str) -> list[AuthorizationRecord]:
        now = datetime.now(timezone.utc).isoformat()
        rows = self._conn.execute(
            """
            SELECT * FROM authorizations
            WHERE device_id = ?
              AND revoked = 0
              AND (expires_at IS NULL OR expires_at > ?)
            """,
            (device_id, now),
        ).fetchall()

        out: list[AuthorizationRecord] = []
        for row in rows:
            out.append(
                AuthorizationRecord(
                    device_id=row["device_id"],
                    consent_type=ConsentType(row["consent_type"]),
                    authorized_by=row["authorized_by"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    evidence_path=Path(row["evidence_path"]),
                    expires_at=(
                        datetime.fromisoformat(row["expires_at"])
                        if row["expires_at"]
                        else None
                    ),
                )
            )
        return out

    def export(self) -> str:
        rows = self._conn.execute("SELECT * FROM authorizations").fetchall()
        return json.dumps([dict(r) for r in rows], indent=2, default=str)

    def close(self) -> None:
        self._conn.close()