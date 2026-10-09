"""All private resource queries bind the verified UUID, including section reads."""
from contextlib import contextmanager

from sqlalchemy import text

from app.db.connection import get_engine
from app.repositories.planner import valid_associations

FIELDS = """r.id,r.subject_id,r.topic_id,s.code AS subject_code,t.title AS topic_title,r.title,
    r.original_filename,r.mime_type,r.file_size_bytes,r.resource_type,r.processing_status,
    r.page_count,r.row_count,r.error_message,r.created_at,r.updated_at"""
JOINS = "FROM public.resources r LEFT JOIN public.subjects s ON s.id=r.subject_id LEFT JOIN public.topics t ON t.id=r.topic_id"


@contextmanager
def transaction():
    with get_engine().begin() as connection:
        yield connection


def get_resource(connection, user_id, resource_id, *, lock=False, private=False):
    fields = FIELDS + (",r.storage_bucket,r.storage_path" if private else "")
    row = connection.execute(text(f"SELECT {fields} {JOINS} WHERE r.user_id=:user_id AND r.id=:id" + (" FOR UPDATE OF r" if lock else "")),
                             {"user_id": user_id, "id": resource_id}).mappings().first()
    return dict(row) if row else None


def list_resources(connection, user_id, *, subject_id=None, topic_id=None, resource_type=None, q=None, limit=50, offset=0):
    where = ["r.user_id=:user_id"]
    params = {"user_id": user_id, "limit": limit, "offset": offset}
    for name, value in (("subject_id", subject_id), ("topic_id", topic_id), ("resource_type", resource_type)):
        if value is not None:
            where.append(f"r.{name}=:{name}")
            params[name] = value
    if q:
        where.append("(r.title ILIKE :q ESCAPE '\\' OR r.original_filename ILIKE :q ESCAPE '\\')")
        params["q"] = "%" + q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
    predicate = " AND ".join(where)
    total = connection.execute(text(f"SELECT count(*) FROM public.resources r WHERE {predicate}"), params).scalar_one()
    rows = connection.execute(text(f"SELECT {FIELDS} {JOINS} WHERE {predicate} ORDER BY r.created_at DESC,r.id DESC LIMIT :limit OFFSET :offset"), params).mappings()
    return {"resources": [dict(row) for row in rows], "total": total}


def insert_resource(connection, user_id, data, sections):
    values = {**data, "user_id": user_id}
    columns = ",".join(values)
    placeholders = ",".join(f":{name}" for name in values)
    connection.execute(text(f"INSERT INTO public.resources ({columns}) VALUES ({placeholders})"), values)
    if sections:
        connection.execute(text("INSERT INTO public.document_sections (user_id,resource_id,page_number,section_index,content) "
                                "VALUES (:user_id,:resource_id,:page_number,:section_index,:content)"),
                           [{**section, "user_id": user_id, "resource_id": data["id"]} for section in sections])
    return get_resource(connection, user_id, data["id"])


def delete_resource(connection, user_id, resource_id):
    connection.execute(text("DELETE FROM public.resources WHERE user_id=:user_id AND id=:id"), {"user_id": user_id, "id": resource_id})


def finish_processing(connection, user_id, resource_id, values, sections):
    params = {key: values[key] for key in ("processing_status", "page_count", "row_count", "error_message")}
    params.update(user_id=user_id, id=resource_id)
    connection.execute(text("UPDATE public.resources SET processing_status=:processing_status, page_count=:page_count, "
                            "row_count=:row_count, error_message=:error_message WHERE user_id=:user_id AND id=:id"), params)
    if sections:
        connection.execute(text("INSERT INTO public.document_sections (user_id,resource_id,page_number,section_index,content) "
                                "VALUES (:user_id,:resource_id,:page_number,:section_index,:content)"),
                           [{**section, "user_id": user_id, "resource_id": resource_id} for section in sections])
    return get_resource(connection, user_id, resource_id)


def mark_processing(connection, user_id, resource_id):
    connection.execute(text("UPDATE public.resources SET processing_status='processing' WHERE user_id=:user_id AND id=:id"),
                       {"user_id": user_id, "id": resource_id})


def content_sections(connection, user_id, resource_id, *, limit=10, offset=0):
    params = {"user_id": user_id, "resource_id": resource_id, "limit": limit, "offset": offset}
    total = connection.execute(text("SELECT count(*) FROM public.document_sections WHERE user_id=:user_id AND resource_id=:resource_id"), params).scalar_one()
    rows = connection.execute(text("SELECT id,page_number,section_index,content FROM public.document_sections "
                                   "WHERE user_id=:user_id AND resource_id=:resource_id ORDER BY section_index,id LIMIT :limit OFFSET :offset"), params).mappings()
    return [dict(row) for row in rows], total
