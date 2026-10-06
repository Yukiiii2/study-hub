"""Bounded weekly recurrence; occurrence identity remains its original local date."""
import re
from functools import wraps
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DAY_CODES = ("MO", "TU", "WE", "TH", "FR", "SA", "SU")


class PlannerError(Exception):
    def __init__(self, detail: str, status_code: int = 422):
        self.detail, self.status_code = detail, status_code
        super().__init__(detail)


def date_bounds(handler):
    @wraps(handler)
    def guarded(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except OverflowError:
            raise PlannerError("These dates exceed the supported calendar boundaries.") from None
    return guarded


def get_zone(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError, TypeError):
        raise PlannerError("A valid IANA timezone is required.") from None


@date_bounds
def localize(value: datetime, zone_name: str) -> datetime:
    zone = get_zone(zone_name)
    naive = value.replace(tzinfo=None)
    candidates = {}
    for fold in (0, 1):
        candidate = naive.replace(tzinfo=zone, fold=fold)
        instant = candidate.astimezone(timezone.utc)
        if instant.astimezone(zone).replace(tzinfo=None) == naive:
            candidates[instant] = candidate
    if len(candidates) != 1:
        raise PlannerError("This local time is invalid or ambiguous in the selected timezone.")
    return next(iter(candidates.values()))


def parse_rule(rule: str, anchor: date):
    match = re.fullmatch(r"FREQ=WEEKLY;BYDAY=((?:MO|TU|WE|TH|FR|SA|SU)(?:,(?:MO|TU|WE|TH|FR|SA|SU))*)(?:;UNTIL=(\d{8}))?", rule)
    if not match:
        raise PlannerError("Use FREQ=WEEKLY;BYDAY=MO,WE with an optional inclusive UNTIL=YYYYMMDD.")
    codes = match.group(1).split(",")
    if len(set(codes)) != len(codes) or DAY_CODES[anchor.weekday()] not in codes:
        raise PlannerError("Select the anchor weekday once in the recurrence rule.")
    try:
        until = datetime.strptime(match.group(2), "%Y%m%d").date() if match.group(2) else None
    except ValueError:
        raise PlannerError("Recurrence end date is invalid.") from None
    if until is not None and until < anchor:
        raise PlannerError("Recurrence end date precedes its start.")
    return {DAY_CODES.index(code) for code in codes}, until


@date_bounds
def validate_range(start_at: datetime, end_at: datetime, *, bounded=True):
    if start_at.tzinfo is None or end_at.tzinfo is None:
        raise PlannerError("Provide an aware, positive date range.")
    start, end = start_at.astimezone(timezone.utc), end_at.astimezone(timezone.utc)
    if end <= start:
        raise PlannerError("Provide an aware, positive date range.")
    if bounded and end - start > timedelta(days=93):
        raise PlannerError("Date ranges cannot exceed 93 days.")


@date_bounds
def validate_event(data: dict):
    validate_range(data["start_at"], data["end_at"], bounded=False)
    zone = get_zone(data["timezone"])
    for name in ("start_at", "end_at"):
        localize(data[name].astimezone(zone), data["timezone"])
    if data.get("topic_id") and not data.get("subject_id"):
        raise PlannerError("A topic requires its subject.")
    if data.get("recurrence_rule"):
        parse_rule(data["recurrence_rule"], data["start_at"].astimezone(zone).date())
        if data["status"] != "scheduled":
            raise PlannerError("Change recurring status on an occurrence; the series stays scheduled.")


@date_bounds
def occurrence(event: dict, day: date) -> dict:
    if not event.get("recurrence_rule"):
        raise PlannerError("This event is not recurring.", 404)
    zone = get_zone(event["timezone"])
    start, end = event["start_at"].astimezone(zone), event["end_at"].astimezone(zone)
    selected, until = parse_rule(event["recurrence_rule"], start.date())
    if day < start.date() or day.weekday() not in selected or (until and day > until):
        raise PlannerError("Occurrence not found.", 404)
    offset = day - start.date()
    generated_start = localize(start.replace(tzinfo=None) + offset, event["timezone"])
    generated_end = localize(end.replace(tzinfo=None) + offset, event["timezone"])
    validate_range(generated_start, generated_end, bounded=False)
    return {**event, "start_at": generated_start,
            "end_at": generated_end,
            "occurrence_date": day, "occurrence_id": None, "is_recurring": True}


def snapshot_response(event: dict, snapshot: dict) -> dict:
    fields = ("subject_id", "topic_id", "title", "event_type", "start_at", "end_at", "status", "notes", "created_at", "updated_at")
    return {**event, **{key: snapshot[key] for key in fields}, "occurrence_date": snapshot["occurrence_date"],
            "occurrence_id": snapshot["id"], "is_recurring": True}


@date_bounds
def expand_events(events: list[dict], snapshots: list[dict], start_at: datetime, end_at: datetime) -> list[dict]:
    validate_range(start_at, end_at)
    by_event = {}
    for snapshot in snapshots:
        by_event.setdefault(snapshot["study_event_id"], {})[snapshot["occurrence_date"]] = snapshot
    rows = []

    def append(row):
        if row["start_at"] < end_at and row["end_at"] > start_at:
            rows.append(row)
            if len(rows) > 2000:
                raise PlannerError("More than 2000 events overlap this range; request a smaller range.")

    for event in events:
        overrides = by_event.get(event["id"], {})
        for snapshot in overrides.values():
            if not snapshot["is_deleted"]:
                append(snapshot_response(event, snapshot))
        if not event.get("recurrence_rule"):
            append({**event, "occurrence_date": None, "occurrence_id": None, "is_recurring": False})
            continue
        zone = get_zone(event["timezone"])
        anchor = event["start_at"].astimezone(zone)
        local_end = event["end_at"].astimezone(zone)
        weekdays, until = parse_rule(event["recurrence_rule"], anchor.date())
        wall_start = start_at.astimezone(zone).replace(tzinfo=None)
        wall_end = end_at.astimezone(zone).replace(tzinfo=None)
        # Include long events anchored before the requested window.
        span = (local_end.replace(tzinfo=None) - anchor.replace(tzinfo=None)).days + 2
        lower = max(anchor.date(), start_at.astimezone(zone).date() - timedelta(days=span))
        upper = end_at.astimezone(zone).date()
        if until:
            upper = min(upper, until)
        day = lower
        while day <= upper:
            if day.weekday() in weekdays and day not in overrides:
                offset = day - anchor.date()
                candidate_start = anchor.replace(tzinfo=None) + offset
                candidate_end = local_end.replace(tzinfo=None) + offset
                # The padded date search includes neighboring days. Do not resolve their
                # DST gaps/folds unless their wall-clock interval can overlap this window.
                if candidate_start < wall_end and candidate_end > wall_start:
                    append(occurrence(event, day))
            if day == date.max:
                break
            day += timedelta(days=1)
    return sorted(rows, key=lambda row: (row["start_at"], str(row["id"])))
