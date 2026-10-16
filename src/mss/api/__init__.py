"""HTTP API layer.

Wraps the use-case layer for internal deployment. Same guarantees apply:
RBAC, authorization gate, audit log. No bypass endpoints exist and none
will be added.
"""

from mss.api.app import create_app

__all__ = ["create_app"]