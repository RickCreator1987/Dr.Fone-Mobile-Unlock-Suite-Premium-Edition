from pathlib import Path

from mss.core.audit import AuditLog


def test_chain_detects_deletion(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    log = AuditLog(path)
    log.append({"event": "a"})
    log.append({"event": "b"})
    log.append({"event": "c"})

    lines = path.read_text(encoding="utf-8").splitlines()
    del lines[1]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    assert log.verify() is False


def test_chain_detects_insertion(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    log = AuditLog(path)
    log.append({"event": "a"})
    log.append({"event": "b"})

    lines = path.read_text(encoding="utf-8").splitlines()
    fake = '{"event":"injected","prev_hash":"0","hash":"0"}'
    lines.insert(1, fake)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    assert log.verify() is False