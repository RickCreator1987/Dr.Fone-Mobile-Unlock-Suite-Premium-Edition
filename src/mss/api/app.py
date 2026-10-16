from __future__ import annotations

from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, status

from mss.api.deps import (
    get_audit,
    get_principal,
    get_store,
)
from mss.api.schemas import (
    AuthorizeBody,
    AuthorizeResponse,
    RevokeBody,
)
from mss.core.audit import AuditLog
from mss.core.authorization import AuthorizationError, ConsentType
from mss.core.rbac import PermissionError_, Principal
from mss.core.store import AuthorizationStore
from mss.use_cases.authorize import AuthorizeDevice, AuthorizeRequest
from mss.use_cases.revoke import RevokeAuthorization, RevokeRequest


def create_app(
    db_path: Path = Path("mss.db"),
    audit_path: Path = Path("audit.jsonl"),
) -> FastAPI:
    app = FastAPI(
        title="Mobile Service Suite",
        version="0.1.0",
        description=(
            "Compliance-first device service API. "
            "No lock-bypass endpoints exist in this service."
        ),
    )

    app.state.db_path = db_path
    app.state.audit_path = audit_path

    @app.get("/healthz")
    def healthz() -> dict:
        return {"ok": True}

    @app.post(
        "/authorizations",
        response_model=AuthorizeResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def grant_authorization(
        body: AuthorizeBody,
        principal: Principal = Depends(get_principal),
        store: AuthorizationStore = Depends(get_store),
        audit: AuditLog = Depends(get_audit),
    ) -> AuthorizeResponse:
        use_case = AuthorizeDevice(store=store, audit=audit)
        try:
            result = use_case.run(
                principal,
                AuthorizeRequest(
                    device_id=body.device_id,
                    consent_type=ConsentType(body.consent_type),
                    authorized_by=body.authorized_by,
                    evidence_path=Path(body.evidence_path),
                ),
            )
        except PermissionError_ as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except AuthorizationError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except FileNotFoundError as exc:
            raise HTTPException(status_code=400, detail=f"evidence not found: {exc}") from exc

        return AuthorizeResponse(
            authorization_id=result.authorization_id,
            evidence_sha256=result.evidence_sha256,
            signature=result.signature,
        )

    @app.post("/authorizations/{authorization_id}/revoke")
    def revoke_authorization(
        authorization_id: int,
        body: RevokeBody,
        principal: Principal = Depends(get_principal),
        store: AuthorizationStore = Depends(get_store),
        audit: AuditLog = Depends(get_audit),
    ) -> dict:
        use_case = RevokeAuthorization(store=store, audit=audit)
        try:
            use_case.run(
                principal,
                RevokeRequest(
                    authorization_id=authorization_id,
                    reason=body.reason,
                ),
            )
        except PermissionError_ as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        return {"revoked": authorization_id}

    @app.get("/devices/{device_id}/authorizations")
    def list_authorizations(
        device_id: str,
        principal: Principal = Depends(get_principal),
        store: AuthorizationStore = Depends(get_store),
    ) -> list[dict]:
        records = store.active_for(device_id)
        return [
            {
                "device_id": r.device_id,
                "consent_type": r.consent_type.value,
                "authorized_by": r.authorized_by,
                "timestamp": r.timestamp.isoformat(),
                "expires_at": r.expires_at.isoformat() if r.expires_at else None,
            }
            for r in records
        ]

    @app.get("/audit/verify")
    def verify_audit(
        principal: Principal = Depends(get_principal),
        audit: AuditLog = Depends(get_audit),
    ) -> dict:
        return {"ok": audit.verify()}

    return app