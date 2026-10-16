"""Uniform error responses.

Every error body is `{"error": ..., "detail": ..., "request_id": ...}`.
No stack traces, no PII, no device data.
"""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse

from mss.core.authorization import AuthorizationError
from mss.core.rbac import PermissionError_


def install_error_handlers(app) -> None:
    @app.exception_handler(PermissionError_)
    async def _perm(request: Request, exc: PermissionError_) -> JSONResponse:
        return _body(403, "forbidden", str(exc), request)

    @app.exception_handler(AuthorizationError)
    async def _authz(request: Request, exc: AuthorizationError) -> JSONResponse:
        return _body(422, "unauthorized_device", str(exc), request)

    @app.exception_handler(FileNotFoundError)
    async def _missing(request: Request, exc: FileNotFoundError) -> JSONResponse:
        return _body(400, "missing_evidence", "evidence file not found", request)


def _body(status: int, error: str, detail: str, request: Request) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "error": error,
            "detail": detail,
            "request_id": getattr(request.state, "request_id", None),
        },
    )