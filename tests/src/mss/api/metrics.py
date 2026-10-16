"""Prometheus metrics.

Counters only. No device ids, no user ids, no evidence paths in labels.
"""

from __future__ import annotations

from prometheus_client import Counter, generate_latest
from starlette.responses import Response


ACTIONS = Counter(
    "mss_actions_total",
    "Device actions attempted",
    ["action", "outcome"],
)

DENIALS = Counter(
    "mss_denials_total",
    "Authorization and permission denials",
    ["reason"],
)

AUDIT_APPENDS = Counter(
    "mss_audit_appends_total",
    "Audit log appends",
)


def metrics_response() -> Response:
    return Response(generate_latest(), media_type="text/plain; version=0.0.4")