from typing import Literal
from unicodedata import category
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.ai_provenance import AIProvenanceDTO

CardStatus = Literal["active", "suspended", "archived"]
ReviewRating = Literal["again", "hard", "good", "easy"]


def clean_text(value, *, multiline=True, required=False):
    if value is None:
        if required:
            raise ValueError("This field cannot be cleared.")
        return None
    if any(category(char) == "Cc" and (not multiline or char not in "\r\n\t") for char in value):
        raise ValueError("Text contains unsupported control characters.")
    value = value.strip()
    if required and not value:
        raise ValueError("Text must be nonblank.")
    return value


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)


class DeckCreate(Input):
    subject_id: UUID | None = None
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)

    @field_validator("title")
    @classmethod
    def valid_title(cls, value):
        return clean_text(value, multiline=False, required=True)

    @field_validator("description")
    @classmethod
    def valid_description(cls, value):
        return clean_text(value)


class DeckPatch(Input):
    subject_id: UUID | None = None
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)

    @field_validator("title")
    @classmethod
    def valid_title(cls, value):
        return clean_text(value, multiline=False, required=True)

    @field_validator("description")
    @classmethod
    def valid_description(cls, value):
        return clean_text(value)


class DeckResponse(DeckCreate):
    id: UUID
    is_archived: bool
    created_at: AwareDatetime
    updated_at: AwareDatetime


class DeckList(BaseModel):
    decks: list[DeckResponse]
    total: int


class CardCreate(Input):
    ai_draft_receipt: str | None = Field(default=None, min_length=1, max_length=2048, strict=True, exclude=True)
    deck_id: UUID | None = None
    subject_id: UUID | None = None
    topic_id: UUID | None = None
    resource_id: UUID | None = None
    source_page: int | None = Field(default=None, strict=True, ge=1, le=200)
    front: str = Field(min_length=1, max_length=5000)
    back: str = Field(min_length=1, max_length=12000)
    notes: str | None = Field(default=None, max_length=5000)
    status: CardStatus = "active"

    @field_validator("front", "back")
    @classmethod
    def valid_content(cls, value):
        return clean_text(value, required=True)

    @field_validator("notes")
    @classmethod
    def valid_notes(cls, value):
        return clean_text(value)

    @model_validator(mode="after")
    def valid_associations(self):
        if self.topic_id is not None and self.subject_id is None:
            raise ValueError("Topic requires a subject.")
        if self.source_page is not None and self.resource_id is None:
            raise ValueError("Source page requires a resource.")
        return self


class CardPatch(Input):
    deck_id: UUID | None = None
    subject_id: UUID | None = None
    topic_id: UUID | None = None
    resource_id: UUID | None = None
    source_page: int | None = Field(default=None, strict=True, ge=1, le=200)
    front: str | None = Field(default=None, min_length=1, max_length=5000)
    back: str | None = Field(default=None, min_length=1, max_length=12000)
    notes: str | None = Field(default=None, max_length=5000)
    status: CardStatus | None = None

    @field_validator("front", "back")
    @classmethod
    def valid_content(cls, value):
        return clean_text(value, required=True)

    @field_validator("notes")
    @classmethod
    def valid_notes(cls, value):
        return clean_text(value)

    @field_validator("status")
    @classmethod
    def valid_status(cls, value):
        if value is None:
            raise ValueError("Status cannot be cleared.")
        return value


class CardResponse(CardCreate):
    ai_provenance: AIProvenanceDTO | None = None
    id: UUID
    interval_days: int = Field(ge=0, le=365)
    next_review_at: AwareDatetime
    review_revision: int = Field(ge=0)
    created_at: AwareDatetime
    updated_at: AwareDatetime


class CardList(BaseModel):
    cards: list[CardResponse]
    total: int


class DueSummary(BaseModel):
    overdue: int
    due_today: int
    upcoming: int


class DueList(CardList):
    summary: DueSummary
    timezone: str
    as_of: AwareDatetime


class ReviewInput(Input):
    rating: ReviewRating
    expected_revision: int = Field(strict=True, ge=0)
    request_id: UUID


class ReviewResponse(BaseModel):
    id: UUID
    flashcard_id: UUID
    request_id: UUID
    previous_revision: int
    reviewed_at: AwareDatetime
    rating: ReviewRating
    previous_interval_days: int
    next_interval_days: int
    next_review_at: AwareDatetime
    algorithm_version: str
    front_snapshot: str
    back_snapshot: str
    created_at: AwareDatetime


class ReviewList(BaseModel):
    reviews: list[ReviewResponse]
    total: int
