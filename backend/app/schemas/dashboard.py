from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.planner import OccurrenceResponse, TaskResponse
from app.schemas.subjects import SubjectResponse
from app.schemas.videos import VideoSummary


class DashboardEvent(OccurrenceResponse):
    subject_code: str | None
    topic_title: str | None


class DashboardTask(TaskResponse):
    subject_code: str | None
    topic_title: str | None


class DashboardSubject(SubjectResponse):
    topic_count: int
    video_count: int
    completed_video_count: int


class DashboardVideoSummary(VideoSummary):
    remaining_videos: int


class DashboardResponse(BaseModel):
    date: date
    timezone: str
    generated_at: datetime
    today_events: list[DashboardEvent]
    upcoming_tasks: list[DashboardTask]
    video_summary: DashboardVideoSummary
    subjects: list[DashboardSubject]
    continue_video_subject_id: UUID | None
