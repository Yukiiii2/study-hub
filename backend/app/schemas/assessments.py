"""Strict assessment authoring and server-owned result DTOs."""
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, Field, field_serializer, field_validator, model_validator

from app.schemas.flashcards import Input, clean_text

AssessmentStatus = Literal["planned", "completed", "cancelled", "archived"]


class AssessmentCreate(Input):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    scheduled_at: AwareDatetime | None = None
    status: AssessmentStatus = "planned"
    topic_ids: list[UUID] = Field(default_factory=list, max_length=500)
    subject_ids: list[UUID] = Field(default_factory=list, max_length=500)

    @field_validator("title")
    @classmethod
    def valid_title(cls, value):
        return clean_text(value, multiline=False, required=True)

    @field_validator("description")
    @classmethod
    def valid_description(cls, value):
        return clean_text(value)

    @field_validator("topic_ids", "subject_ids")
    @classmethod
    def unique_ids(cls, value):
        if value is None or len(value) != len(set(value)):
            raise ValueError("Coverage must contain unique IDs and cannot be cleared to null.")
        return value


class AssessmentPatch(AssessmentCreate):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    status: AssessmentStatus | None = None
    topic_ids: list[UUID] | None = Field(default=None, max_length=500)
    subject_ids: list[UUID] | None = Field(default=None, max_length=500)

    @field_validator("status")
    @classmethod
    def valid_status(cls, value):
        if value is None:
            raise ValueError("Status cannot be cleared.")
        return value


class CoverageTopic(BaseModel):
    id: UUID
    subject_id: UUID
    code: str | None
    title: str


class CoverageSubject(BaseModel):
    id: UUID
    code: str
    name: str
    scope: Literal["all_topics", "selected_topics"]


class AssessmentResponse(AssessmentCreate):
    id: UUID
    created_at: AwareDatetime
    updated_at: AwareDatetime
    coverage_topics: list[CoverageTopic]
    coverage_subjects: list[CoverageSubject]
    topic_count: int


class Readiness(BaseModel):
    topic_count: int
    total_videos: int
    completed_videos: int
    video_completion_percentage: Decimal | None
    quiz_graded_answers: int
    quiz_correct_answers: int
    quiz_accuracy_percentage: Decimal | None
    active_flashcards: int
    reviewed_flashcards: int
    due_flashcards: int
    overdue_flashcards: int
    as_of: AwareDatetime
    timezone: str

    @field_serializer("video_completion_percentage", "quiz_accuracy_percentage", when_used="json")
    def numeric_json(self, value):
        return float(value) if value is not None else None


class AssessmentDetail(AssessmentResponse):
    readiness: Readiness


class AssessmentList(BaseModel):
    assessments: list[AssessmentResponse]
    total: int


class AttemptPatch(Input):
    started_at: AwareDatetime | None = None
    completed_at: AwareDatetime | None = None
    score: Decimal | None = Field(default=None, allow_inf_nan=False, max_digits=18, decimal_places=4)
    max_score: Decimal | None = Field(default=None, allow_inf_nan=False, max_digits=18, decimal_places=4)
    notes: str | None = Field(default=None, max_length=5000)

    @field_validator("score", "max_score", mode="before")
    @classmethod
    def reject_boolean_score(cls, value):
        if isinstance(value, bool):
            raise ValueError("Score must be a number.")
        return value

    @field_validator("notes")
    @classmethod
    def valid_notes(cls, value):
        return clean_text(value)


class AttemptCreate(AttemptPatch):
    @model_validator(mode="after")
    def valid_result(self):
        if (self.score is None) != (self.max_score is None):
            raise ValueError("Score and maximum score must be supplied together.")
        if self.score is not None:
            if self.score < 0 or self.max_score <= 0 or self.score > self.max_score or self.completed_at is None:
                raise ValueError("A completed result requires a nonnegative score within a positive maximum.")
        if self.started_at is not None and self.completed_at is not None and self.completed_at < self.started_at:
            raise ValueError("Completion cannot precede the start.")
        return self


class AttemptResponse(AttemptCreate):
    id: UUID
    assessment_id: UUID
    percentage: Decimal | None
    created_at: AwareDatetime
    updated_at: AwareDatetime

    @field_serializer("score", "max_score", "percentage", when_used="json")
    def numeric_json(self, value):
        return float(value) if value is not None else None


class AttemptList(BaseModel):
    attempts: list[AttemptResponse]
    total: int
