"""Read-only dashboard aggregates; no curriculum/progress rows are created."""
from contextlib import contextmanager
from uuid import UUID

from sqlalchemy import bindparam, text

from app.db.connection import get_engine
from app.repositories.planner import TASK_FIELDS


@contextmanager
def snapshot():
    with get_engine().begin() as connection:
        # One consistent, read-only snapshot across curriculum, progress and planner queries.
        connection.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY"))
        yield connection


def subject_counts(connection, user_id: UUID):
    # Aggregate topics and lectures separately so joining them cannot multiply counts.
    return [dict(row) for row in connection.execute(text("""
        WITH topic_counts AS (
            SELECT subject_id, count(*) AS topic_count
            FROM public.topics GROUP BY subject_id
        ), lecture_counts AS (
            SELECT t.subject_id, count(*) AS video_count,
                   count(*) FILTER (WHERE p.status = 'completed') AS completed_video_count,
                   COALESCE(sum(v.duration_seconds), 0) AS total_duration_seconds,
                   COALESCE(sum(v.duration_seconds) FILTER (WHERE p.status = 'completed'), 0) AS completed_duration_seconds,
                   count(*) FILTER (WHERE v.duration_seconds IS NULL) AS unknown_duration_videos,
                   count(*) FILTER (WHERE p.status = 'in_progress') AS in_progress_videos
            FROM public.videos v JOIN public.topics t ON t.id = v.topic_id
            LEFT JOIN public.user_video_progress p ON p.video_id = v.id AND p.user_id = :user_id
            GROUP BY t.subject_id
        )
        SELECT s.id, s.code, s.name, s.display_order, s.color_key,
               COALESCE(tc.topic_count, 0) AS topic_count,
               COALESCE(lc.video_count, 0) AS video_count,
               COALESCE(lc.completed_video_count, 0) AS completed_video_count,
               COALESCE(lc.total_duration_seconds, 0) AS total_duration_seconds,
               COALESCE(lc.completed_duration_seconds, 0) AS completed_duration_seconds,
               COALESCE(lc.unknown_duration_videos, 0) AS unknown_duration_videos,
               COALESCE(lc.in_progress_videos, 0) AS in_progress_videos
        FROM public.subjects s
        LEFT JOIN topic_counts tc ON tc.subject_id = s.id
        LEFT JOIN lecture_counts lc ON lc.subject_id = s.id
        WHERE s.is_active ORDER BY s.display_order, s.code, s.id
    """), {"user_id": user_id}).mappings()]


def pending_tasks(connection, user_id: UUID):
    return [dict(row) for row in connection.execute(text(f"""
        SELECT {TASK_FIELDS} FROM public.study_tasks
        WHERE user_id = :user_id AND status = 'pending'
        ORDER BY due_at ASC NULLS LAST, created_at, id LIMIT 5
    """), {"user_id": user_id}).mappings()]


def curriculum_labels(connection, records):
    def labels(table, field, ids):
        if not ids:
            return {}
        # Table/field names come only from the fixed calls below, never HTTP input.
        query = text(f"SELECT id, {field} FROM public.{table} WHERE id IN :ids").bindparams(bindparam("ids", expanding=True))
        return {row["id"]: row[field] for row in connection.execute(query, {"ids": list(ids)}).mappings()}
    subjects = labels("subjects", "code", {r["subject_id"] for r in records if r["subject_id"]})
    topics = labels("topics", "title", {r["topic_id"] for r in records if r["topic_id"]})
    return subjects, topics
