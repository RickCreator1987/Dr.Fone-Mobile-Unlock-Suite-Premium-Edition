from pathlib import Path

from mss.core.migrations import migrate


def test_migrate_applies_all(tmp_path: Path) -> None:
    db = tmp_path / "mss.db"
    applied = migrate(db)
    assert applied >= 1

    # Second run should be a no-op
    applied_again = migrate(db)
    assert applied_again == 0