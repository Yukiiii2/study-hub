"""Read-only actual and planned study metrics; no inferred progress scores."""
from datetime import date
from uuid import UUID

from pydantic import BaseModel

from app.schemas.planner import ActivityType, SessionResponse


class LabeledSessionResponse(SessionResponse):
    subject_code: str | None
    subject_title: str | None
    topic_title: str | None


class SessionHistoryResponse(BaseModel):
    sessions: list[LabeledSessionResponse]
    total: int
    limit: int
    offset: int


class StudySummary(BaseModel):
    total_seconds: int
    session_count: int
    active_days: int
    average_session_seconds: float
    longest_session_seconds: int
    planned_seconds: int


class DailyActivity(BaseModel):
    date: date
    duration_seconds: int
    session_count: int


class SubjectActivity(BaseModel):
    subject_id: UUID | None
    subject_code: str | None
    subject_title: str | None
    subject_color_key: str | None = None
    duration_seconds: int
    session_count: int
    planned_seconds: int


class ActivityBreakdown(BaseModel):
    activity_type: ActivityType
    duration_seconds: int
    session_count: int


class AnalyticsResponse(BaseModel):
    timezone: str
    start_date: date
    end_date: date
    summary: StudySummary
    daily: list[DailyActivity]
    subjects: list[SubjectActivity]
    activities: list[ActivityBreakdown]
