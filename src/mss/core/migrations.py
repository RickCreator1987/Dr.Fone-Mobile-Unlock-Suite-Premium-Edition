from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Migration:
    version: int
    description: str
    sql: str


MIGRATIONS: list[Migration] = [
    Migration(
        version=1,
        description="create authorizations table",
        sql="""
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
        """,
    ),
    Migration(
        version=2,
        description="create devices table",
        sql="""
        CREATE TABLE IF NOT EXISTS devices (
            device_id TEXT PRIMARY KEY,
            platform TEXT NOT NULL,
            owner TEXT NOT NULL,
            notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        );
        """,
    ),
    Migration(
        version=3,
        description="create operators table",
        sql="""
        CREATE TABLE IF NOT EXISTS operators (
            user_id TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            roles TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """,
    ),
]


def _ensure_version_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    conn.commit()


def _current_version(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT MAX(version) AS v FROM schema_version").fetchone()
    return int(row["v"] or 0)


def migrate(db_path: Path) -> int:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        _ensure_version_table(conn)
        current = _current_version(conn)
        applied = 0
        for migration in sorted(MIGRATIONS, key=lambda m: m.version):
            if migration.version <= current:
                continue
            conn.executescript(migration.sql)
            conn.execute(
                "INSERT INTO schema_version (version) VALUES (?)",
                (migration.version,),
            )
            conn.commit()
            applied += 1
        return applied
    finally:
        conn.close()