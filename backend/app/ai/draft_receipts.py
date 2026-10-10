"""Transient, owner-bound draft receipts; never contain generated study text."""
import base64
import hashlib
import hmac
import json
import re
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.core.config import get_settings
from app.schemas.ai_provenance import AIProvenanceDTO

MAX_RECEIPT_LENGTH = 2048
RECEIPT_LIFETIME_SECONDS = 24 * 60 * 60
_PURPOSE = b"cpa-study-hub/ai-draft-receipt/v1"


class DraftReceiptError(Exception):
    def __init__(self, status_code=400):
        self.status_code = status_code
        self.detail = "AI draft receipt is invalid or expired. Generate a new draft."
        super().__init__(self.detail)


class _Receipt(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)

    version: Literal[1]
    user_id: UUID
    kind: Literal["question", "flashcard"]
    issued_at: int = Field(strict=True, ge=0)
    expires_at: int = Field(strict=True, ge=0)
    provenance: AIProvenanceDTO

    @field_validator("version", mode="before")
    @classmethod
    def strict_version(cls, value):
        if type(value) is not int:
            raise ValueError("Invalid AI receipt.")
        return value


def _now():
    return datetime.now(timezone.utc)


def _signing_key():
    secret = get_settings().supabase_secret_key.get_secret_value()
    if not secret:
        raise DraftReceiptError(503)
    return hmac.digest(secret.encode("utf-8"), _PURPOSE, "sha256")


def _encode(value):
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def mint_draft_receipt(user_id, kind, *, provider, model, generated_at,
                       subject_id=None, topic_id=None, resource_id=None, source_pages=(),
                       attempt_id=None, question_id=None):
    """Issue a receipt only after server source and provider-output validation."""
    issued_at = int(_now().timestamp())
    try:
        provenance = AIProvenanceDTO(provider=provider, model=model, generated_at=generated_at,
                                    subject_id=subject_id, topic_id=topic_id, resource_id=resource_id,
                                    source_pages=list(source_pages), attempt_id=attempt_id, question_id=question_id)
        receipt = _Receipt(version=1, user_id=user_id, kind=kind, issued_at=issued_at,
                           expires_at=issued_at + RECEIPT_LIFETIME_SECONDS, provenance=provenance)
        if not issued_at - 60 <= provenance.generated_at.timestamp() <= issued_at + 60:
            raise DraftReceiptError()
        payload = _encode(json.dumps(receipt.model_dump(mode="json"), sort_keys=True,
                                     separators=(",", ":"), ensure_ascii=True).encode("utf-8"))
        token = payload + "." + _encode(hmac.digest(_signing_key(), payload.encode("ascii"), "sha256"))
        if len(token) > MAX_RECEIPT_LENGTH:
            raise DraftReceiptError()
        return token
    except (ValidationError, ValueError, TypeError, OverflowError):
        raise DraftReceiptError() from None


def verify_draft_receipt(receipt, user_id, kind):
    """Return signed origin metadata, allowing editable content before confirmation."""
    try:
        if not isinstance(receipt, str) or not 1 <= len(receipt) <= MAX_RECEIPT_LENGTH:
            raise DraftReceiptError()
        if not re.fullmatch(r"[A-Za-z0-9_-]+\.[A-Za-z0-9_-]{43}", receipt):
            raise DraftReceiptError()
        payload, signature = receipt.split(".")
        expected = _encode(hmac.digest(_signing_key(), payload.encode("ascii"), "sha256"))
        if not hmac.compare_digest(signature, expected):
            raise DraftReceiptError()
        decoded = base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4))
        data = _Receipt.model_validate_json(decoded)
        now = int(_now().timestamp())
        if (data.user_id != UUID(str(user_id)) or data.kind != kind or
                data.expires_at - data.issued_at != RECEIPT_LIFETIME_SECONDS or
                not data.issued_at <= now < data.expires_at or
                not data.issued_at - 60 <= data.provenance.generated_at.timestamp() <= data.issued_at + 60):
            raise DraftReceiptError()
        return data.provenance
    except (ValidationError, ValueError, TypeError, OverflowError):
        raise DraftReceiptError() from None
