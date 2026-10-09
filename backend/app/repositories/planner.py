"""Owner-scoped planner SQL. Table/field interpolation is exclusively fixed code."""
from contextlib import contextmanager
from uuid import UUID

from sqlalchemy import text

from app.db.connection import get_engine

EVENT_FIELDS = "id, subject_id, topic_id, title, event_type, start_at, end_at, timezone, status, recurrence_rule, notes, created_at, updated_at"
TASK_FIELDS = "id, subject_id, topic_id, title, task_type, estimated_minutes, due_at, status, scheduled_event_id, created_at, updated_at"
SESSION_FIELDS = "id, study_event_id, occurrence_id, subject_id, topic_id, activity_type, started_at, ended_at, duration_seconds, notes, created_at"
SNAPSHOT_FIELDS = "id, study_event_id, occurrence_date, subject_id, topic_id, title, event_type, start_at, end_at, status, notes, is_deleted, created_at, updated_at"
TABLES = {"events": ("study_events", EVENT_FIELDS), "tasks": ("study_tasks", TASK_FIELDS),
          "sessions": ("study_sessions", SESSION_FIELDS), "occurrences": ("study_event_occurrences", SNAPSHOT_FIELDS)}
WRITABLE = {
    "events": {"subject_id", "topic_id", "title", "event_type", "start_at", "end_at", "timezone", "status", "recurrence_rule", "notes"},
    "tasks": {"subject_id", "topic_id", "title", "task_type", "estimated_minutes", "due_at", "status", "scheduled_event_id"},
    "sessions": {"study_event_id", "occurrence_id", "subject_id", "topic_id", "activity_type", "notes"},
    "occurrences": {"study_event_id", "occurrence_date", "subject_id", "topic_id", "title", "event_type", "start_at", "end_at", "status", "notes", "is_deleted"},
}


@contextmanager
def transaction():
    with get_engine().begin() as connection:
        yield connection


def get_record(connection, kind: str, user_id: UUID, record_id: UUID, *, lock=False):
    table, fields = TABLES[kind]
    row = connection.execute(text(f"SELECT {fields} FROM public.{table} WHERE user_id=:user_id AND id=:id" + (" FOR UPDATE" if lock else "")),
                             {"user_id": user_id, "id": record_id}).mappings().first()
    return dict(row) if row else None


def insert_record(connection, kind: str, user_id: UUID, data: dict):
    table, fields = TABLES[kind]
    values = {key: value for key, value in data.items() if key in WRITABLE[kind]}
    values["user_id"] = user_id
    columns = ", ".join(values)
    placeholders = ", ".join(f":{key}" for key in values)
    row = connection.execute(text(f"INSERT INTO public.{table} ({columns}) VALUES ({placeholders}) RETURNING {fields}"), values).mappings().one()
    return dict(row)


def update_record(connection, kind: str, user_id: UUID, record_id: UUID, data: dict):
    table, fields = TABLES[kind]
    values = {key: value for key, value in data.items() if key in WRITABLE[kind]}
    if not values:
        return get_record(connection, kind, user_id, record_id)
    setters = ", ".join(f"{key}=:{key}" for key in values)
    row = connection.execute(text(f"UPDATE public.{table} SET {setters} WHERE user_id=:user_id AND id=:id RETURNING {fields}"),
                             {**values, "user_id": user_id, "id": record_id}).mappings().first()
    return dict(row) if row else None


def delete_record(connection, kind: str, user_id: UUID, record_id: UUID):
    table, _ = TABLES[kind]
    return connection.execute(text(f"DELETE FROM public.{table} WHERE user_id=:user_id AND id=:id"),
                              {"user_id": user_id, "id": record_id}).rowcount > 0


def profile_timezone(connection, user_id: UUID):
    return connection.execute(text("SELECT timezone FROM public.profiles WHERE id=:user_id"), {"user_id": user_id}).scalar_one()


def valid_associations(connection, subject_id, topic_id):
    if subject_id is None:
        return topic_id is None
    params = {"subject_id": subject_id, "topic_id": topic_id}
    if topic_id is None:
        return connection.execute(text("SELECT 1 FROM public.subjects WHERE id=:subject_id AND is_active FOR SHARE"), params).first() is not None
    return connection.execute(text("SELECT 1 FROM public.topics t JOIN public.subjects s ON s.id=t.subject_id "
                                   "WHERE t.id=:topic_id AND s.id=:subject_id AND s.is_active FOR SHARE OF t,s"), params).first() is not None


def event_range(connection, user_id, start_at, end_at):
    rows = connection.execute(text(f"SELECT {EVENT_FIELDS} FROM public.study_events e WHERE user_id=:user_id AND "
        "(recurrence_rule IS NOT NULL OR (start_at < :end_at AND end_at > :start_at) OR EXISTS "
        "(SELECT 1 FROM public.study_event_occurrences o WHERE o.user_id=:user_id AND o.study_event_id=e.id "
        "AND NOT o.is_deleted AND o.start_at < :end_at AND o.end_at > :start_at))"),
        {"user_id": user_id, "start_at": start_at, "end_at": end_at}).mappings()
    events = [dict(row) for row in rows]
    snapshots = connection.execute(text(f"SELECT {SNAPSHOT_FIELDS} FROM public.study_event_occurrences WHERE user_id=:user_id"),
                                   {"user_id": user_id}).mappings()
    return events, [dict(row) for row in snapshots]


def get_snapshot(connection, user_id, event_id, day):
    row = connection.execute(text(f"SELECT {SNAPSHOT_FIELDS} FROM public.study_event_occurrences "
                                  "WHERE user_id=:user_id AND study_event_id=:event_id AND occurrence_date=:day FOR UPDATE"),
                             {"user_id": user_id, "event_id": event_id, "day": day}).mappings().first()
    return dict(row) if row else None


def has_snapshots(connection, user_id, event_id):
    return connection.execute(text("SELECT 1 FROM public.study_event_occurrences WHERE user_id=:user_id AND study_event_id=:event_id LIMIT 1"),
                              {"user_id": user_id, "event_id": event_id}).first() is not None


def list_tasks(connection, user_id):
    return [dict(row) for row in connection.execute(text(f"SELECT {TASK_FIELDS} FROM public.study_tasks WHERE user_id=:user_id ORDER BY created_at DESC, id"),
                                                   {"user_id": user_id}).mappings()]


def active_session(connection, user_id):
    row = connection.execute(text(f"SELECT {SESSION_FIELDS} FROM public.study_sessions WHERE user_id=:user_id AND ended_at IS NULL"),
                             {"user_id": user_id}).mappings().first()
    return dict(row) if row else None


def list_sessions(connection, user_id, start_at=None, end_at=None):
    predicates, params = [], {"user_id": user_id}
    if start_at is not None:
        predicates.append("COALESCE(ended_at, now()) > :start_at")
        params["start_at"] = start_at
    if end_at is not None:
        predicates.append("started_at < :end_at")
        params["end_at"] = end_at
    extra = " AND " + " AND ".join(predicates) if predicates else ""
    return [dict(row) for row in connection.execute(text(f"SELECT {SESSION_FIELDS} FROM public.study_sessions WHERE user_id=:user_id{extra} ORDER BY started_at DESC,id DESC LIMIT 100"), params).mappings()]


def stop_session(connection, user_id, session_id, notes_data):
    notes_sql = ", notes=:notes" if "notes" in notes_data else ""
    row = connection.execute(text(f"WITH stopped AS MATERIALIZED (SELECT clock_timestamp() AS instant) "
        "UPDATE public.study_sessions SET ended_at=COALESCE(ended_at, GREATEST(started_at, stopped.instant)), "
        "duration_seconds=COALESCE(duration_seconds, GREATEST(0, FLOOR(EXTRACT(EPOCH FROM (stopped.instant-started_at)))::integer))"
        f"{notes_sql} FROM stopped WHERE user_id=:user_id AND id=:id RETURNING {SESSION_FIELDS}"),
        {"user_id": user_id, "id": session_id, **notes_data}).mappings().one()
    return dict(row)
