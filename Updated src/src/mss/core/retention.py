"""Retention and deletion.

Deletes expired authorizations and their evidence files. Every deletion is
audited. Audit log entries themselves are never deleted by this module.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from mss.core.audit import AuditLog


@dataclass
class RetentionReport:
    authorizations_deleted: int
    evidence_deleted: int
    evidence_missing: int


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_retention(
    db_path: Path,
    audit: AuditLog,
    *,
    operator: str = "system",
    delete_evidence: bool = True,
) -> RetentionReport:
    db_path = Path(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT id, device_id, evidence_path
            FROM authorizations
            WHERE (expires_at IS NOT NULL AND expires_at <= ?)
               OR revoked = 1
            """,
            (_now_iso(),),
        ).fetchall()

        evidence_deleted = 0
        evidence_missing = 0

        for row in rows:
            path = Path(row["evidence_path"])
            if delete_evidence:
                if path.exists():
                    path.unlink()
                    evidence_deleted += 1
                else:
                    evidence_missing += 1

            conn.execute("DELETE FROM authorizations WHERE id = ?", (row["id"],))
            audit.append(
                {
                    "event": "authorization_deleted",
                    "authorization_id": row["id"],
                    "device_id": row["device_id"],
                    "operator": operator,
                }
            )

        conn.commit()
        return RetentionReport(
            authorizations_deleted=len(rows),
            evidence_deleted=evidence_deleted,
            evidence_missing=evidence_missing,
        )
    finally:
        conn.close()