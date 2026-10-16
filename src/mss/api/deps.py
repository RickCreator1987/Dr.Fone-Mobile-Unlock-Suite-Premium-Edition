from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import Header, HTTPException, Request

from mss.core.audit import AuditLog
from mss.core.rbac import Principal, Role
from mss.core.store import AuthorizationStore


def get_store(request: Request) -> AuthorizationStore:
    return AuthorizationStore(request.app.state.db_path)


def get_audit(request: Request) -> AuditLog:
    return AuditLog(request.app.state.audit_path)


def get_principal(
    x_mss_user: str = Header(default=""),
    x_mss_roles: str = Header(default="viewer"),
) -> Principal:
    if not x_mss_user:
        raise HTTPException(status_code=401, detail="missing X-MSS-User")

    try:
        roles = frozenset(Role(r) for r in json.loads(x_mss_roles))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"bad X-MSS-Roles: {exc}") from exc

    return Principal(user_id=x_mss_user, roles=roles)