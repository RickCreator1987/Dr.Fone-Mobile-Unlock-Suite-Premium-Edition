from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from mss.core.rbac import Principal, Role


@dataclass(frozen=True)
class Operator:
    user_id: str
    display_name: str
    roles: frozenset[Role]

    def to_principal(self) -> Principal:
        return Principal(user_id=self.user_id, roles=self.roles)


class OperatorStore:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row

    def upsert(self, operator: Operator) -> None:
        self._conn.execute(
            """
            INSERT INTO operators (user_id, display_name, roles, created_at)
            VALUES (?, ?, ?, datetime('now'))
            ON CONFLICT(user_id) DO UPDATE SET
              display_name = excluded.display_name,
              roles = excluded.roles
            """,
            (
                operator.user_id,
                operator.display_name,
                json.dumps(sorted(r.value for r in operator.roles)),
            ),
        )
        self._conn.commit()

    def get(self, user_id: str) -> Operator | None:
        row = self._conn.execute(
            "SELECT * FROM operators WHERE user_id = ?", (user_id,)
        ).fetchone()
        if not row:
            return None
        roles = frozenset(Role(r) for r in json.loads(row["roles"]))
        return Operator(
            user_id=row["user_id"],
            display_name=row["display_name"],
            roles=roles,
        )

    def close(self) -> None:
        self._conn.close()