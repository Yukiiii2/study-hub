"""Restore actual study state with profile-local completed-time totals."""
from datetime import datetime, timezone
from uuid import UUID

from app.repositories import analytics as analytics_repo, planner as repo
from app.schemas.focus import FocusResponse
from app.services.analytics import local_day_range
from app.services.planner_recurrence import get_zone


def get_focus(user_id: UUID, *, now: datetime | None = None) -> FocusResponse:
    now = now or datetime.now(timezone.utc)
    with analytics_repo.snapshot() as connection:
        zone_name = repo.profile_timezone(connection, user_id)
        day = now.astimezone(get_zone(zone_name)).date()
        start, end = local_day_range(day, zone_name)
        active = repo.active_session(connection, user_id)
        totals = analytics_repo.aggregate_sessions(connection, user_id, start, end)
        recent = analytics_repo.list_labeled_sessions(connection, user_id, limit=10)
        return FocusResponse.model_validate({
            "timezone": zone_name,
            "server_now": now,
            "active_session": active,
            "today_seconds": totals["total_seconds"],
            "today_session_count": totals["session_count"],
            "recent_sessions": recent["sessions"],
        })
