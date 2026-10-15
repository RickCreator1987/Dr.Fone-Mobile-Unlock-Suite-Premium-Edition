from pathlib import Path

from mss.core.audit import AuditLog


def test_audit_chain_valid(tmp_path: Path) -> None:
    log = AuditLog(tmp_path / "audit.jsonl")
    log.append({"event": "one"})
    log.append({"event": "two"})
    assert log.verify() is True


def test_audit_tamper_detected(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    log = AuditLog(path)
    log.append({"event": "one"})
    log.append({"event": "two"})

    lines = path.read_text(encoding="utf-8").splitlines()
    lines[0] = lines[0].replace('"one"', '"tampered"')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    assert log.verify() is False