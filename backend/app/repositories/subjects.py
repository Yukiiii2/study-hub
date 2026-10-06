from sqlalchemy import text

from app.db.connection import get_engine
from app.schemas.subjects import SubjectResponse


def list_subjects() -> list[SubjectResponse]:
    with get_engine().connect() as connection:
        rows = connection.execute(text(
            "SELECT id, code, name, display_order, color_key, is_active, created_at, updated_at "
            "FROM public.subjects ORDER BY display_order, code"
        )).mappings()
        return [SubjectResponse.model_validate(row) for row in rows]
