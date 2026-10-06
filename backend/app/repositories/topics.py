from uuid import UUID

from sqlalchemy import text

from app.db.connection import get_engine
from app.schemas.topics import TopicResponse

TOPIC_FIELDS = "t.id, t.subject_id, t.parent_topic_id, t.code, t.title, t.description, t.display_order"


def list_topics(subject_id: UUID) -> list[TopicResponse]:
    with get_engine().connect() as connection:
        rows = connection.execute(text(
            f"SELECT {TOPIC_FIELDS} FROM public.topics t "
            "JOIN public.subjects s ON s.id = t.subject_id "
            "WHERE t.subject_id = :subject_id AND s.is_active "
            "ORDER BY t.display_order, t.title, t.id"
        ), {"subject_id": subject_id}).mappings()
        return [TopicResponse.model_validate(row) for row in rows]


def get_topic(topic_id: UUID) -> TopicResponse | None:
    with get_engine().connect() as connection:
        row = connection.execute(text(
            f"SELECT {TOPIC_FIELDS} FROM public.topics t "
            "JOIN public.subjects s ON s.id = t.subject_id "
            "WHERE t.id = :topic_id AND s.is_active"
        ), {"topic_id": topic_id}).mappings().first()
        return TopicResponse.model_validate(row) if row else None
