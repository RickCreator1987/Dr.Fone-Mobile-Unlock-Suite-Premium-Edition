from __future__ import annotations

from pydantic import BaseModel, Field


class AuthorizeBody(BaseModel):
    device_id: str = Field(min_length=1)
    consent_type: str = Field(default="owner")
    authorized_by: str = Field(min_length=1)
    evidence_path: str = Field(min_length=1)


class AuthorizeResponse(BaseModel):
    authorization_id: int
    evidence_sha256: str
    signature: str | None = None


class RevokeBody(BaseModel):
    reason: str = Field(min_length=1)