from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from mss.core.audit import AuditLog
from mss.core.authorization import (
    AuthorizationError,
    AuthorizationGate,
    AuthorizationRecord,
    ConsentType,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mss",
        description="Compliance-first mobile service suite",
    )
    parser.add_argument("--audit-log", default="audit.jsonl")
    sub = parser.add_subparsers(dest="cmd", required=True)

    verify = sub.add_parser("verify-authorization", help="Check authorization for a device")
    verify.add_argument("device_id")
    verify.add_argument("--evidence", required=True)
    verify.add_argument("--authorized-by", required=True)
    verify.add_argument(
        "--consent-type",
        choices=[c.value for c in ConsentType],
        default=ConsentType.OWNER.value,
    )

    sub.add_parser("verify-audit", help="Verify audit log integrity")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    audit = AuditLog(Path(args.audit_log))

    if args.cmd == "verify-authorization":
        record = AuthorizationRecord(
            device_id=args.device_id,
            consent_type=ConsentType(args.consent_type),
            authorized_by=args.authorized_by,
            timestamp=datetime.now(timezone.utc),
            evidence_path=Path(args.evidence),
        )
        gate = AuthorizationGate([record])

        try:
            gate.require(args.device_id)
        except AuthorizationError as exc:
            audit.append(
                {
                    "event": "authorization_denied",
                    "device_id": args.device_id,
                    "reason": str(exc),
                }
            )
            print(f"DENIED: {exc}", file=sys.stderr)
            return 1

        audit.append(
            {
                "event": "authorization_granted",
                "device_id": args.device_id,
                "authorized_by": args.authorized_by,
            }
        )
        print("AUTHORIZED")
        return 0

    if args.cmd == "verify-audit":
        ok = audit.verify()
        print("OK" if ok else "TAMPERED")
        return 0 if ok else 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())