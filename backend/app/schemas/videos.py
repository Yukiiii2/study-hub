from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

ProgressStatus = Literal["not_started", "in_progress", "completed"]


class ProgressUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: ProgressStatus


class VideoResponse(BaseModel):
    id: UUID
    topic_id: UUID
    topic_code: str | None
    topic_title: str
    title: str
    duration_seconds: int | None
    display_order: int
    status: ProgressStatus
    watched_seconds: int | None
    completed_at: datetime | None


class VideoSummary(BaseModel):
    total_videos: int
    completed_videos: int
    total_duration_seconds: int
    completed_duration_seconds: int
    remaining_duration_seconds: int
    unknown_duration_videos: int


class SubjectVideosResponse(BaseModel):
    videos: list[VideoResponse]
    summary: VideoSummary
