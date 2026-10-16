from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from mss.api.app import create_app
from mss.core.authorization import AuthorizationRecord, ConsentType
from mss.core.store import AuthorizationStore


def _client(tmp_path: Path) -> TestClient:
    app = create_app(
        db_path=tmp_path / "mss.db",
        audit_path=tmp_path / "audit.jsonl",
    )
    return TestClient(app)


def _seed_authorization(tmp_path: Path) -> int:
    store = AuthorizationStore(tmp_path / "mss.db")
    evidence = tmp_path / "consent.pdf"
    evidence.write_text("signed", encoding="utf-8")
    auth_id = store.add(
        AuthorizationRecord(
            device_id="dev-1",
            consent_type=ConsentType.OWNER,
            authorized_by="owner@example.com",
            timestamp=datetime.now(timezone.utc),
            evidence_path=evidence,
        )
    )
    store.close()
    return auth_id


def test_revoke_requires_reviewer(tmp_path: Path) -> None:
    auth_id = _seed_authorization(tmp_path)
    c = _client(tmp_path)

    r = c.post(
        f"/authorizations/{auth_id}/revoke",
        headers={"X-MSS-User": "tech1", "X-MSS-Roles": '["technician"]'},
        json={"reason": "owner changed mind"},
    )
    assert r.status_code == 403


def test_revoke_happy_path(tmp_path: Path) -> None:
    auth_id = _seed_authorization(tmp_path)
    c = _client(tmp_path)

    r = c.post(
        f"/authorizations/{auth_id}/revoke",
        headers={"X-MSS-User": "reviewer1", "X-MSS-Roles": '["reviewer"]'},
        json={"reason": "owner changed mind"},
    )
    assert r.status_code == 200, r.text
    assert r.json() == {"revoked": auth_id}

    store = AuthorizationStore(tmp_path / "mss.db")
    assert store.active_for("dev-1") == []