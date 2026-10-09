"""Owner-scoped SQL aggregates and bounded completed-session history."""
from contextlib import contextmanager

from sqlalchemy import bindparam, text

from app.db.connection import get_engine
from app.repositories import planner


@contextmanager
def snapshot():
    with get_engine().begin() as connection:
        connection.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY"))
        yield connection


def clipped_seconds(start, end):
    # Integer cumulative offsets reconcile every midnight fragment with the stored
    # floored elapsed duration, including subsecond starts and clipped boundaries.
    return (f"(LEAST(duration_seconds, FLOOR(EXTRACT(EPOCH FROM ({end} - started_at)))) "
            f"- LEAST(duration_seconds, FLOOR(EXTRACT(EPOCH FROM ({start} - started_at)))))::bigint")


COMPLETED_RANGE = """
    WITH completed AS (
        SELECT id, subject_id, activity_type, started_at, ended_at, duration_seconds,
               GREATEST(started_at, :start_at) AS clip_start,
               LEAST(ended_at, :end_at) AS clip_end
        FROM public.study_sessions
        WHERE user_id = :user_id AND ended_at IS NOT NULL AND duration_seconds IS NOT NULL
          AND :start_at < :end_at AND started_at < :end_at AND ended_at > :start_at
    ), clipped AS (
        SELECT *, """ + clipped_seconds("clip_start", "clip_end") + """ AS seconds FROM completed
    )
"""


def range_params(user_id, start_at, end_at):
    return {"user_id": user_id, "start_at": start_at, "end_at": end_at}


def aggregate_sessions(connection, user_id, start_at, end_at):
    return dict(connection.execute(text(COMPLETED_RANGE + """
        SELECT COALESCE(sum(seconds), 0) AS total_seconds, count(*) AS session_count,
               COALESCE(avg(seconds), 0) AS average_session_seconds,
               COALESCE(max(seconds), 0) AS longest_session_seconds FROM clipped
    """), range_params(user_id, start_at, end_at)).mappings().one())


def session_breakdowns(connection, user_id, start_at, end_at):
    params = range_params(user_id, start_at, end_at)
    subjects = [dict(row) for row in connection.execute(text(COMPLETED_RANGE + """
        SELECT c.subject_id, s.code AS subject_code, s.name AS subject_title,
               s.color_key AS subject_color_key,
               sum(c.seconds) AS duration_seconds, count(*) AS session_count
        FROM clipped c LEFT JOIN public.subjects s ON s.id = c.subject_id
        GROUP BY c.subject_id, s.code, s.name, s.color_key, s.display_order
        ORDER BY s.display_order NULLS LAST, s.code, c.subject_id
    """), params).mappings()]
    activities = [dict(row) for row in connection.execute(text(COMPLETED_RANGE + """
        SELECT activity_type, sum(seconds) AS duration_seconds, count(*) AS session_count
        FROM clipped GROUP BY activity_type ORDER BY activity_type
    """), params).mappings()]
    return subjects, activities


def daily_sessions(connection, user_id, windows):
    # At most 90 prevalidated local-day windows. Only aggregate rows cross the
    # database boundary; arbitrary amounts of completed history stay in SQL.
    params = range_params(user_id, windows[0][1], windows[-1][2])
    values = []
    for index, (day, start, end) in enumerate(windows):
        values.append(f"(CAST(:day{index} AS date), CAST(:start{index} AS timestamptz), CAST(:end{index} AS timestamptz))")
        params.update({f"day{index}": day, f"start{index}": start, f"end{index}": end})
    duration = clipped_seconds("GREATEST(c.started_at, d.day_start)", "LEAST(c.ended_at, d.day_end)")
    query = COMPLETED_RANGE + ", days(day, day_start, day_end) AS (VALUES " + ", ".join(values) + ") " + f"""
        SELECT d.day AS date, COALESCE(sum({duration}), 0) AS duration_seconds,
               count(c.id) AS session_count
        FROM days d LEFT JOIN completed c ON d.day_start < d.day_end
          AND c.started_at < d.day_end AND c.ended_at > d.day_start
        GROUP BY d.day ORDER BY d.day
    """
    return [dict(row) for row in connection.execute(text(query), params).mappings()]


def subject_labels(connection, ids):
    if not ids:
        return {}
    query = text("SELECT id, code, name, color_key FROM public.subjects WHERE id IN :ids").bindparams(bindparam("ids", expanding=True))
    return {row["id"]: (row["code"], row["name"], row["color_key"]) for row in connection.execute(query, {"ids": list(ids)}).mappings()}


def list_labeled_sessions(connection, user_id, start_at=None, end_at=None, limit=20, offset=0):
    params = {"user_id": user_id, "limit": limit, "offset": offset}
    predicates = ["ss.user_id = :user_id", "ss.ended_at IS NOT NULL", "ss.duration_seconds IS NOT NULL"]
    if start_at is not None:
        predicates.append("ss.ended_at > :start_at")
        params["start_at"] = start_at
    if end_at is not None:
        predicates.append("ss.started_at < :end_at")
        params["end_at"] = end_at
    if start_at is not None and end_at is not None:
        predicates.append(":start_at < :end_at")
    where = " AND ".join(predicates)
    total = connection.execute(text(f"SELECT count(*) FROM public.study_sessions ss WHERE {where}"), params).scalar_one()
    fields = ", ".join("ss." + field.strip() for field in planner.SESSION_FIELDS.split(","))
    sessions = [dict(row) for row in connection.execute(text(f"""
        SELECT {fields}, s.code AS subject_code, s.name AS subject_title, t.title AS topic_title
        FROM public.study_sessions ss
        LEFT JOIN public.subjects s ON s.id = ss.subject_id
        LEFT JOIN public.topics t ON t.id = ss.topic_id
        WHERE {where} ORDER BY ss.started_at DESC, ss.id DESC LIMIT :limit OFFSET :offset
    """), params).mappings()]
    return {"sessions": sessions, "total": total, "limit": limit, "offset": offset}
