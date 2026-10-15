from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from pathlib import Path

CHUNK = 65536


@dataclass(frozen=True)
class ConsentArtifact:
    path: Path
    sha256: str
    size_bytes: int


def hash_file(path: Path) -> ConsentArtifact:
    if not path.exists():
        raise FileNotFoundError(path)
    h = hashlib.sha256()
    size = 0
    with path.open("rb") as f:
        while chunk := f.read(CHUNK):
            h.update(chunk)
            size += len(chunk)
    return ConsentArtifact(path=path, sha256=h.hexdigest(), size_bytes=size)


def sign_artifact(artifact: ConsentArtifact, key: bytes) -> str:
    payload = json.dumps(
        {"sha256": artifact.sha256, "size": artifact.size_bytes},
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hmac.new(key, payload, hashlib.sha256).hexdigest()


def verify_signature(artifact: ConsentArtifact, key: bytes, signature: str) -> bool:
    return hmac.compare_digest(sign_artifact(artifact, key), signature)