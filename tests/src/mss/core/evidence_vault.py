"""Evidence vault.

Moves consent evidence into an append-only directory with a content-addressed
name so it cannot be silently overwritten.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from mss.core.consent import hash_file


@dataclass(frozen=True)
class StoredEvidence:
    original_path: Path
    stored_path: Path
    sha256: str


class EvidenceVault:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def store(self, source: Path) -> StoredEvidence:
        artifact = hash_file(source)
        target_dir = self.root / artifact.sha256[:2]
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / artifact.sha256

        if not target.exists():
            shutil.copy2(source, target)
            target.chmod(0o440)

        return StoredEvidence(
            original_path=source,
            stored_path=target,
            sha256=artifact.sha256,
        )