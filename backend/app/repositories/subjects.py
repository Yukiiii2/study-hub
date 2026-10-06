from sqlalchemy import text
from uuid import UUID

from app.db.connection import get_engine
from app.schemas.subjects import SubjectResponse


def list_subjects() -> list[SubjectResponse]:
    with get_engine().connect() as connection:
        rows = connection.execute(text(
            "SELECT id, code, name, display_order, color_key "
            "FROM public.subjects WHERE is_active ORDER BY display_order, code, id"
        )).mappings()
        return [SubjectResponse.model_validate(row) for row in rows]


def get_subject(subject_id: UUID) -> SubjectResponse | None:
    with get_engine().connect() as connection:
        row = connection.execute(text(
            "SELECT id, code, name, display_order, color_key FROM public.subjects "
            "WHERE id = :subject_id AND is_active"
        ), {"subject_id": subject_id}).mappings().first()
        return SubjectResponse.model_validate(row) if row else None
