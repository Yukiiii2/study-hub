from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class UploadMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)

    title: str | None = Field(default=None, max_length=200)
    subject_id: UUID | None = None
    topic_id: UUID | None = None

    @field_validator("title")
    @classmethod
    def trim_title(cls, value):
        if value is None:
            return None
        value = value.strip()
        if not value or any(ord(c) < 32 for c in value):
            raise ValueError("Title must be nonblank and contain no control characters.")
        return value

    @model_validator(mode="after")
    def matching_subject(self):
        if self.topic_id is not None and self.subject_id is None:
            raise ValueError("Topic requires a subject.")
        return self


class ResourceResponse(BaseModel):
    id: UUID
    subject_id: UUID | None
    topic_id: UUID | None
    subject_code: str | None
    topic_title: str | None
    title: str
    original_filename: str
    mime_type: str
    file_size_bytes: int
    resource_type: Literal["pdf", "csv"]
    processing_status: Literal["uploaded", "processing", "ready", "failed"]
    page_count: int | None
    row_count: int | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime


class ResourceList(BaseModel):
    resources: list[ResourceResponse]
    total: int


class ResourceSection(BaseModel):
    id: UUID
    page_number: int
    section_index: int
    content: str


class ResourceContent(BaseModel):
    resource: ResourceResponse
    sections: list[ResourceSection]
    headers: list[str]
    rows: list[list[str]]
    row_count: int | None
    total_sections: int


class ResourceDownload(BaseModel):
    url: str
    expires_in: Literal[120] = 120
