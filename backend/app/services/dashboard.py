"""Dashboard reads compose the existing curriculum, lecture and planner domains."""
from datetime import datetime, time, timedelta, timezone
from uuid import UUID

from app.repositories import dashboard as repo, planner as planner_repo
from app.schemas.dashboard import (
    DashboardEvent, DashboardResponse, DashboardSubject, DashboardTask, DashboardVideoSummary,
)
from app.services.planner_recurrence import expand_events, get_zone


def today_range(now: datetime, zone_name: str):
    zone = get_zone(zone_name)
    day = now.astimezone(zone).date()
    start = datetime.combine(day, time.min, zone).astimezone(timezone.utc)
    end = datetime.combine(day + timedelta(days=1), time.min, zone).astimezone(timezone.utc)
    return day, start, end


def get_dashboard(user_id: UUID, *, now: datetime | None = None) -> DashboardResponse:
    now = now or datetime.now(timezone.utc)
    with repo.snapshot() as connection:
        zone_name = planner_repo.profile_timezone(connection, user_id)
        day, start, end = today_range(now, zone_name)
        subjects = repo.subject_counts(connection, user_id)
        events, snapshots = planner_repo.event_range(connection, user_id, start, end)
        today_events = expand_events(events, snapshots, start, end)
        tasks = repo.pending_tasks(connection, user_id)
        subject_labels, topic_labels = repo.curriculum_labels(connection, [*today_events, *tasks])

    def context(row):
        return {**row, "subject_code": subject_labels.get(row["subject_id"]), "topic_title": topic_labels.get(row["topic_id"])}

    total_videos = sum(row["video_count"] for row in subjects)
    completed_videos = sum(row["completed_video_count"] for row in subjects)
    total_duration = sum(row["total_duration_seconds"] for row in subjects)
    completed_duration = sum(row["completed_duration_seconds"] for row in subjects)
    continue_subject = next((row for row in subjects if row["in_progress_videos"] > 0), None)
    if continue_subject is None:
        continue_subject = next((row for row in subjects if row["video_count"] > row["completed_video_count"]), None)
    return DashboardResponse(
        date=day, timezone=zone_name, generated_at=now,
        today_events=[DashboardEvent.model_validate(context(row)) for row in today_events],
        upcoming_tasks=[DashboardTask.model_validate(context(row)) for row in tasks],
        subjects=[DashboardSubject.model_validate(row) for row in subjects],
        video_summary=DashboardVideoSummary(
            total_videos=total_videos, completed_videos=completed_videos, remaining_videos=total_videos - completed_videos,
            total_duration_seconds=total_duration, completed_duration_seconds=completed_duration,
            remaining_duration_seconds=total_duration - completed_duration,
            unknown_duration_videos=sum(row["unknown_duration_videos"] for row in subjects),
        ),
        continue_video_subject_id=continue_subject["id"] if continue_subject else None,
    )
