"""Profile-local study ranges and canonical, independent actual/planned metrics."""
from datetime import date, datetime, time, timedelta, timezone
from math import floor

from app.repositories import analytics as repo
from app.repositories import planner
from app.schemas.analytics import AnalyticsResponse, SessionHistoryResponse
from app.services.planner_recurrence import PlannerError, date_bounds, expand_events, get_zone


@date_bounds
def local_date_boundary(day: date, timezone_name: str):
    """First instant of a calendar date, allowing midnight folds/gaps.

    Event wall times retain planner's strict localization. Calendar dates use
    their earliest midnight on folds and the transition instant on gaps. A
    skipped date shares the next date's boundary and therefore has zero time.
    """
    zone = get_zone(timezone_name)
    midnight = datetime.combine(day, time.min)
    candidates = sorted({midnight.replace(tzinfo=zone, fold=fold).astimezone(timezone.utc)
                         for fold in (0, 1)})
    valid = [instant for instant in candidates
             if instant.astimezone(zone).replace(tzinfo=None) == midnight]
    if valid:
        return valid[0]
    # Invalid midnight lies inside an offset jump. Binary search its two fold
    # projections to locate the actual transition, including partial-hour gaps.
    lower, upper = candidates[0], candidates[-1]
    if lower.astimezone(zone).date() >= day or upper.astimezone(zone).date() < day:
        raise PlannerError("These dates exceed the supported calendar boundaries.")
    while upper - lower > timedelta(microseconds=1):
        middle = lower + (upper - lower) // 2
        if middle.astimezone(zone).date() < day:
            lower = middle
        else:
            upper = middle
    return upper


@date_bounds
def local_day_range(day: date, timezone_name: str):
    start = local_date_boundary(day, timezone_name)
    end = local_date_boundary(day + timedelta(days=1), timezone_name)
    return start, end


@date_bounds
def analytics_range(timezone_name, period=7, start_date=None, end_date=None, now=None):
    now = now or datetime.now(timezone.utc)
    today = now.astimezone(get_zone(timezone_name)).date()
    if period not in (7, 30, 90):
        raise PlannerError("Select a 7, 30 or 90 day period.")
    if (start_date is None) != (end_date is None):
        raise PlannerError("Provide both start_date and end_date for a custom range.")
    if start_date is None:
        start_date, end_date = today - timedelta(days=period - 1), today
    if end_date < start_date or (end_date - start_date).days >= 90 or end_date > today:
        raise PlannerError("Choose a positive range of at most 90 inclusive days ending today or earlier.")
    start, _ = local_day_range(start_date, timezone_name)
    _, end = local_day_range(end_date, timezone_name)
    return start_date, end_date, start, end


@date_bounds
def day_windows(start_date, end_date, timezone_name):
    return [(day, *local_day_range(day, timezone_name))
            for day in (start_date + timedelta(days=offset)
                        for offset in range((end_date - start_date).days + 1))]


def planned_seconds(events, snapshots, start_at, end_at):
    if start_at == end_at:
        return {}
    by_subject = {}
    for event in expand_events(events, snapshots, start_at, end_at):
        if event["status"] == "cancelled":
            continue
        start = event["start_at"].astimezone(timezone.utc)
        end = event["end_at"].astimezone(timezone.utc)
        seconds = floor((min(end, end_at) - max(start, start_at)).total_seconds())
        subject_id = event["subject_id"]
        by_subject[subject_id] = by_subject.get(subject_id, 0) + seconds
    return by_subject


def get_summary(user_id, period=7, start_date=None, end_date=None, *, now=None):
    with repo.snapshot() as connection:
        timezone_name = planner.profile_timezone(connection, user_id)
        start_date, end_date, start_at, end_at = analytics_range(timezone_name, period, start_date, end_date, now)
        windows = day_windows(start_date, end_date, timezone_name)
        summary = repo.aggregate_sessions(connection, user_id, start_at, end_at)
        daily = repo.daily_sessions(connection, user_id, windows)
        subjects, activities = repo.session_breakdowns(connection, user_id, start_at, end_at)
        events, snapshots = planner.event_range(connection, user_id, start_at, end_at)
        plans = planned_seconds(events, snapshots, start_at, end_at)
        by_subject = {row["subject_id"]: {**row, "planned_seconds": plans.pop(row["subject_id"], 0)} for row in subjects}
        labels = repo.subject_labels(connection, {key for key in plans if key is not None})
        for subject_id, seconds in plans.items():
            code, title, color_key = labels.get(subject_id, (None, None, None))
            by_subject[subject_id] = {"subject_id": subject_id, "subject_code": code, "subject_title": title,
                                      "subject_color_key": color_key,
                                      "duration_seconds": 0, "session_count": 0, "planned_seconds": seconds}
        subjects = sorted(by_subject.values(), key=lambda row: (row["subject_id"] is None, row["subject_code"] or ""))
        summary.update(active_days=sum(day["duration_seconds"] > 0 for day in daily),
                       planned_seconds=sum(row["planned_seconds"] for row in subjects))
        return AnalyticsResponse(timezone=timezone_name, start_date=start_date, end_date=end_date,
                                 summary=summary, daily=daily, subjects=subjects, activities=activities)


def get_sessions(user_id, period=7, start_date=None, end_date=None, limit=20, offset=0, *, now=None):
    with repo.snapshot() as connection:
        timezone_name = planner.profile_timezone(connection, user_id)
        _, _, start_at, end_at = analytics_range(timezone_name, period, start_date, end_date, now)
        return SessionHistoryResponse(**repo.list_labeled_sessions(connection, user_id, start_at, end_at, limit, offset))
