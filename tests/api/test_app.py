from pathlib import Path

from fastapi.testclient import TestClient

from mss.api.app import create_app


def _client(tmp_path: Path) -> TestClient:
    app = create_app(
        db_path=tmp_path / "mss.db",
        audit_path=tmp_path / "audit.jsonl",
    )
    return TestClient(app)


def test_healthz(tmp_path: Path) -> None:
    c = _client(tmp_path)
    assert c.get("/healthz").json() == {"ok": True}


def test_missing_user_header(tmp_path: Path) -> None:
    c = _client(tmp_path)
    r = c.get("/audit/verify")
    assert r.status_code == 401


def test_grant_authorization(tmp_path: Path) -> None:
    evidence = tmp_path / "consent.pdf"
    evidence.write_text("signed", encoding="utf-8")

    c = _client(tmp_path)
    r = c.post(
        "/authorizations",
        headers={
            "X-MSS-User": "admin1",
            "X-MSS-Roles": '["admin"]',
        },
        json={
            "device_id": "dev-1",
            "consent_type": "owner",
            "authorized_by": "owner@example.com",
            "evidence_path": str(evidence),
        },
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["authorization_id"] >= 1
    assert len(body["evidence_sha256"]) == 64


def test_viewer_cannot_grant(tmp_path: Path) -> None:
    evidence = tmp_path / "consent.pdf"
    evidence.write_text("signed", encoding="utf-8")

    c = _client(tmp_path)
    r = c.post(
        "/authorizations",
        headers={
            "X-MSS-User": "viewer1",
            "X-MSS-Roles": '["viewer"]',
        },
        json={
            "device_id": "dev-1",
            "consent_type": "owner",
            "authorized_by": "owner@example.com",
            "evidence_path": str(evidence),
        },
    )
    assert r.status_code == 403