
---

## `src/mss/api/middleware.py`

```python
"""Request middleware.

Adds a request id and emits one redacted access log line per request.
Never logs request bodies; those can contain PII or evidence paths.
"""

from __future__ import annotations

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from mss.core.redact import redact

log = logging.getLogger("mss.access")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-Id") or uuid.uuid4().hex
        request.state.request_id = request_id

        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000

        response.headers["X-Request-Id"] = request_id

        user = request.headers.get("X-MSS-User", "-")
        path = redact(request.url.path)
        query = redact(str(request.url.query)) if request.url.query else ""

        log.info(
            "req id=%s user=%s method=%s path=%s query=%s status=%d ms=%.1f",
            request_id,
            user,
            request.method,
            path,
            query,
            response.status_code,
            elapsed_ms,
        )
        return response