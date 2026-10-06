from uuid import UUID
from sqlalchemy import text

from app.db.connection import get_engine
from app.schemas.videos import ProgressStatus, VideoResponse

VIDEO_QUERY = """
    SELECT v.id, v.topic_id, t.code AS topic_code, t.title AS topic_title,
           v.title, v.duration_seconds, v.display_order,
           COALESCE(p.status, 'not_started') AS status, p.watched_seconds, p.completed_at
    FROM public.videos v
    JOIN public.topics t ON t.id = v.topic_id
    JOIN public.subjects s ON s.id = t.subject_id
    LEFT JOIN public.user_video_progress p ON p.video_id = v.id AND p.user_id = :user_id
    WHERE s.is_active
"""


def list_videos(user_id: UUID, *, topic_id: UUID | None = None, subject_id: UUID | None = None) -> list[VideoResponse]:
    # Only fixed repository predicates can be composed; request values stay parameterized.
    if topic_id is not None:
        predicate, params = " AND v.topic_id = :topic_id", {"topic_id": topic_id}
    elif subject_id is not None:
        predicate, params = " AND t.subject_id = :subject_id", {"subject_id": subject_id}
    else:
        raise ValueError("A topic or subject is required")
    with get_engine().connect() as connection:
        rows = connection.execute(text(VIDEO_QUERY + predicate + " ORDER BY t.display_order, t.id, v.display_order, v.id"),
                                  {"user_id": user_id, **params}).mappings()
        return [VideoResponse.model_validate(row) for row in rows]


def update_progress(video_id: UUID, user_id: UUID, status: ProgressStatus) -> VideoResponse | None:
    with get_engine().begin() as connection:
        available = connection.execute(text(
            "SELECT v.id FROM public.videos v JOIN public.topics t ON t.id = v.topic_id "
            "JOIN public.subjects s ON s.id = t.subject_id WHERE v.id = :video_id AND s.is_active FOR SHARE OF v, s"
        ), {"video_id": video_id}).first()
        if available is None:
            return None
        params = {"video_id": video_id, "user_id": user_id, "status": status}
        if status == "not_started":
            # Resetting untouched lectures does not manufacture a progress record.
            connection.execute(text(
                "UPDATE public.user_video_progress SET status = 'not_started', watched_seconds = NULL, "
                "started_at = NULL, completed_at = NULL WHERE video_id = :video_id AND user_id = :user_id"
            ), params)
        else:
            connection.execute(text("""
                INSERT INTO public.user_video_progress(user_id, video_id, status, started_at, completed_at)
                VALUES (:user_id, :video_id, :status, now(), CASE WHEN :status = 'completed' THEN now() END)
                ON CONFLICT (user_id, video_id) DO UPDATE SET status = EXCLUDED.status,
                    started_at = COALESCE(user_video_progress.started_at, EXCLUDED.started_at),
                    completed_at = CASE WHEN EXCLUDED.status = 'completed'
                        THEN COALESCE(user_video_progress.completed_at, EXCLUDED.completed_at) ELSE NULL END
            """), params)
        row = connection.execute(text(VIDEO_QUERY + " AND v.id = :video_id"), params).mappings().one()
        return VideoResponse.model_validate(row)
