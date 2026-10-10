"""Read-only context retrieval. Every private query binds the verified owner."""
from contextlib import contextmanager

from sqlalchemy import text

from app.db.connection import get_engine
from app.repositories.resources import get_resource
from app.repositories.quizzes import get_attempt, answers


@contextmanager
def read_context():
    with get_engine().connect() as connection:
        yield connection


def curriculum(connection, subject_id, topic_id):
    topic = None
    if topic_id:
        row = connection.execute(text("SELECT t.id,t.subject_id,left(t.title,500) AS title,left(t.description,2000) AS description FROM public.topics t "
                                      "JOIN public.subjects s ON s.id=t.subject_id WHERE t.id=:id AND s.is_active"), {"id": topic_id}).mappings().first()
        topic = dict(row) if row else None
        if not topic or (subject_id and subject_id != topic["subject_id"]):
            return None
        subject_id = topic["subject_id"]
    subject = None
    if subject_id:
        row = connection.execute(text("SELECT id,code,left(name,500) AS name FROM public.subjects WHERE id=:id AND is_active"), {"id": subject_id}).mappings().first()
        subject = dict(row) if row else None
        if not subject:
            return None
    return {"subject": subject, "topic": topic}


def passages(connection, user_id, resource_id, terms, *, allow_first=False, source_page=None):
    params = {"user_id": user_id, "resource_id": resource_id}
    positions = []
    for index, term in enumerate(terms):
        params[f"term{index}"] = term
        positions.append(f"nullif(strpos(lower(content),:term{index}),0)")
    match = " OR ".join(f"{position} IS NOT NULL" for position in positions) or "FALSE"
    score = "+".join(f"CASE WHEN {position} IS NOT NULL THEN 1 ELSE 0 END" for position in positions) or "0::integer"
    start = f"greatest(1,coalesce(least({','.join(positions)}),1)-300)" if positions else "1"
    predicate = "user_id=:user_id AND resource_id=:resource_id"
    if source_page:
        params["source_page"] = source_page
        predicate += " AND page_number=:source_page"
    if not allow_first:
        predicate += f" AND ({match})"
    rows = connection.execute(text(f"SELECT id,page_number,substring(content FROM {start} FOR 1800) AS content "
                                   f"FROM public.document_sections WHERE {predicate} "
                                   f"ORDER BY ({score}) DESC,section_index,id LIMIT 6"), params).mappings()
    return [dict(row) for row in rows if row["content"].strip()]
