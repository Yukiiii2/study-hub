"""Read-only metadata for the original AI draft, even after user edits."""
from typing import Annotated
from unicodedata import category
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator, model_validator


class AIProvenanceDTO(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)

    provider: str = Field(min_length=1, max_length=40, strict=True)
    model: str = Field(min_length=1, max_length=160, strict=True)
    generated_at: AwareDatetime
    subject_id: UUID | None = None
    topic_id: UUID | None = None
    resource_id: UUID | None = None
    source_pages: list[Annotated[int, Field(strict=True, ge=1, le=200)]] = Field(default_factory=list, max_length=6)
    attempt_id: UUID | None = None
    question_id: UUID | None = None

    @field_validator("provider", "model")
    @classmethod
    def valid_label(cls, value):
        if not value.strip() or any(category(char) == "Cc" for char in value):
            raise ValueError("Invalid AI metadata.")
        return value

    @model_validator(mode="after")
    def valid_sources(self):
        if self.topic_id is not None and self.subject_id is None:
            raise ValueError("Invalid AI metadata.")
        if self.source_pages and self.resource_id is None:
            raise ValueError("Invalid AI metadata.")
        if len(set(self.source_pages)) != len(self.source_pages):
            raise ValueError("Invalid AI metadata.")
        if (self.attempt_id is None) != (self.question_id is None):
            raise ValueError("Invalid AI metadata.")
        return self
