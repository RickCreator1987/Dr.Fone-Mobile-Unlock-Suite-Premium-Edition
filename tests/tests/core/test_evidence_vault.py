from pathlib import Path

from mss.core.evidence_vault import EvidenceVault


def test_vault_is_content_addressed(tmp_path: Path) -> None:
    src = tmp_path / "consent.pdf"
    src.write_text("hello", encoding="utf-8")

    vault = EvidenceVault(tmp_path / "vault")
    a = vault.store(src)
    b = vault.store(src)

    assert a.sha256 == b.sha256
    assert a.stored_path == b.stored_path
    assert a.stored_path.exists()
    # Second store must not duplicate
    assert len(list((tmp_path / "vault").rglob("*"))) == 2  # dir + file