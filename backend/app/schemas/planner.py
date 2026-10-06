from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator, model_validator

EventType = Literal["lecture", "reading", "drill", "recall", "quiz", "assessment", "general"]
EventStatus = Literal["scheduled", "completed", "skipped", "cancelled"]
TaskStatus = Literal["pending", "scheduled", "completed", "cancelled"]
EditableTaskStatus = Literal["pending", "completed", "cancelled"]


class Request(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @field_validator("title", check_fields=False)
    @classmethod
    def nonblank_title(cls, value):
        if value is not None:
            value = value.strip()
            if not value:
                raise ValueError("Title cannot be blank.")
        return value


class EventCreate(Request):
    subject_id: UUID | None = None
    topic_id: UUID | None = None
    title: str = Field(max_length=200)
    event_type: EventType = "general"
    start_at: AwareDatetime
    end_at: AwareDatetime
    timezone: str | None = None
    status: EventStatus = "scheduled"
    recurrence_rule: str | None = None
    notes: str | None = Field(default=None, max_length=10000)


class OccurrencePatch(Request):
    subject_id: UUID | None = None
    topic_id: UUID | None = None
    title: str | None = Field(default=None, max_length=200)
    event_type: EventType | None = None
    start_at: AwareDatetime | None = None
    end_at: AwareDatetime | None = None
    status: EventStatus | None = None
    notes: str | None = Field(default=None, max_length=10000)

    @model_validator(mode="after")
    def required_values_not_null(self):
        for name in {"title", "event_type", "start_at", "end_at", "status"} & self.model_fields_set:
            if getattr(self, name) is None:
                raise ValueError(f"{name} cannot be null.")
        return self


class EventPatch(OccurrencePatch):
    timezone: str | None = None
    recurrence_rule: str | None = None

    @model_validator(mode="after")
    def timezone_not_null(self):
        if "timezone" in self.model_fields_set and self.timezone is None:
            raise ValueError("timezone cannot be null.")
        return self


class EventResponse(BaseModel):
    id: UUID
    subject_id: UUID | None
    topic_id: UUID | None
    title: str
    event_type: EventType
    start_at: datetime
    end_at: datetime
    timezone: str
    status: EventStatus
    recurrence_rule: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class OccurrenceResponse(EventResponse):
    occurrence_date: date | None = None
    is_recurring: bool
    occurrence_id: UUID | None = None


class TaskCreate(Request):
    subject_id: UUID | None = None
    topic_id: UUID | None = None
    title: str = Field(max_length=200)
    task_type: EventType = "general"
    estimated_minutes: int | None = Field(default=None, gt=0, strict=True)
    due_at: AwareDatetime | None = None
    status: EditableTaskStatus = "pending"


class TaskPatch(Request):
    subject_id: UUID | None = None
    topic_id: UUID | None = None
    title: str | None = Field(default=None, max_length=200)
    task_type: EventType | None = None
    estimated_minutes: int | None = Field(default=None, gt=0, strict=True)
    due_at: AwareDatetime | None = None
    status: EditableTaskStatus | None = None

    @model_validator(mode="after")
    def required_values_not_null(self):
        for name in {"title", "task_type", "status"} & self.model_fields_set:
            if getattr(self, name) is None:
                raise ValueError(f"{name} cannot be null.")
        return self


class TaskResponse(BaseModel):
    id: UUID
    subject_id: UUID | None
    topic_id: UUID | None
    title: str
    task_type: EventType
    estimated_minutes: int | None
    due_at: datetime | None
    status: TaskStatus
    scheduled_event_id: UUID | None
    created_at: datetime
    updated_at: datetime


class SessionCreate(Request):
    study_event_id: UUID | None = None
    occurrence_date: date | None = None
    subject_id: UUID | None = None
    topic_id: UUID | None = None
    notes: str | None = Field(default=None, max_length=10000)


class SessionPatch(Request):
    action: Literal["stop"] | None = None
    notes: str | None = Field(default=None, max_length=10000)

    @model_validator(mode="after")
    def require_edit(self):
        if not self.model_fields_set or ("action" in self.model_fields_set and self.action is None):
            raise ValueError("Provide stop action or notes.")
        return self


class SessionResponse(BaseModel):
    id: UUID
    study_event_id: UUID | None
    occurrence_id: UUID | None
    subject_id: UUID | None
    topic_id: UUID | None
    started_at: datetime
    ended_at: datetime | None
    duration_seconds: int | None
    notes: str | None
    created_at: datetime


class PlannerContext(BaseModel):
    timezone: str
    active_session: SessionResponse | None
