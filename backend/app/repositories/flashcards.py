"""Bounded, owner-scoped flashcard SQL; fixed field lists hide ownership in DTOs."""
from contextlib import contextmanager
import json

from sqlalchemy import text

from app.db.connection import get_engine
from app.repositories.planner import profile_timezone, valid_associations
from app.repositories.quizzes import valid_resource

DECK_FIELDS = "id,subject_id,title,description,is_archived,created_at,updated_at"
CARD_FIELDS = "id,deck_id,subject_id,topic_id,resource_id,source_page,front,back,notes,status,ai_provenance,interval_days,next_review_at,review_revision,created_at,updated_at"
REVIEW_FIELDS = "id,flashcard_id,request_id,previous_revision,reviewed_at,rating,previous_interval_days,next_interval_days,next_review_at,algorithm_version,front_snapshot,back_snapshot,created_at"
TABLES = {"deck": ("flashcard_decks", DECK_FIELDS), "card": ("flashcards", CARD_FIELDS)}
WRITABLE = {"deck": {"subject_id", "title", "description"},
            "card": {"deck_id", "subject_id", "topic_id", "resource_id", "source_page", "front", "back", "notes", "status"}}


@contextmanager
def transaction():
    with get_engine().begin() as connection:
        yield connection


def get_record(connection, kind, user_id, record_id, *, lock=None):
    table, fields = TABLES[kind]
    suffix = {None: "", "update": " FOR UPDATE", "share": " FOR SHARE"}[lock]
    row = connection.execute(text(f"SELECT {fields} FROM public.{table} WHERE user_id=:user_id AND id=:id" + suffix),
                             {"user_id": user_id, "id": record_id}).mappings().first()
    return dict(row) if row else None


def insert_record(connection, kind, user_id, data, *, now=None):
    table, fields = TABLES[kind]
    values = {key: value for key, value in data.items() if key in WRITABLE[kind]}
    values["user_id"] = user_id
    if kind == "card":
        values["next_review_at"] = now
        if data.get("ai_provenance") is not None:
            values["ai_provenance"] = json.dumps(data["ai_provenance"])
    columns = ",".join(values)
    placeholders = ",".join("CAST(:ai_provenance AS jsonb)" if key == "ai_provenance" else f":{key}" for key in values)
    row = connection.execute(text(f"INSERT INTO public.{table}({columns}) VALUES ({placeholders}) RETURNING {fields}"), values).mappings().one()
    return dict(row)


def update_record(connection, kind, user_id, record_id, data):
    table, fields = TABLES[kind]
    values = {key: value for key, value in data.items() if key in WRITABLE[kind]}
    if not values:
        return get_record(connection, kind, user_id, record_id)
    setters = ",".join(f"{key}=:{key}" for key in values)
    if kind == "card":
        setters += ",review_revision=review_revision+1"
    row = connection.execute(text(f"UPDATE public.{table} SET {setters} WHERE user_id=:user_id AND id=:id RETURNING {fields}"),
                             {**values, "user_id": user_id, "id": record_id}).mappings().one()
    return dict(row)


def archive_card(connection, user_id, card_id):
    connection.execute(text("UPDATE public.flashcards SET status='archived',review_revision=review_revision+1 "
                            "WHERE user_id=:user_id AND id=:id AND status<>'archived'"), {"user_id": user_id, "id": card_id})


def archive_deck(connection, user_id, deck_id):
    # The caller holds the deck lock; card association writes acquire it first.
    connection.execute(text("SELECT id FROM public.flashcards WHERE user_id=:user_id AND deck_id=:id ORDER BY id FOR UPDATE"),
                       {"user_id": user_id, "id": deck_id}).all()
    connection.execute(text("UPDATE public.flashcards SET deck_id=NULL,review_revision=review_revision+1 WHERE user_id=:user_id AND deck_id=:id"),
                       {"user_id": user_id, "id": deck_id})
    connection.execute(text("UPDATE public.flashcard_decks SET is_archived=true WHERE user_id=:user_id AND id=:id AND NOT is_archived"),
                       {"user_id": user_id, "id": deck_id})


def deck_subject_conflicts(connection, user_id, deck_id, subject_id):
    if subject_id is None:
        return False
    return connection.execute(text("SELECT EXISTS(SELECT 1 FROM public.flashcards WHERE user_id=:user_id AND deck_id=:id "
                                   "AND subject_id IS DISTINCT FROM :subject_id)"),
                              {"user_id": user_id, "id": deck_id, "subject_id": subject_id}).scalar_one()


def _search(where, params, fields, q):
    if q:
        where.append("(" + " OR ".join(f"{field} ILIKE :q ESCAPE '\\'" for field in fields) + ")")
        params["q"] = "%" + q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"


def list_decks(connection, user_id, *, subject_id=None, q=None, limit=50, offset=0):
    where = ["user_id=:user_id", "NOT is_archived"]
    params = {"user_id": user_id, "limit": limit, "offset": offset}
    if subject_id is not None:
        where.append("subject_id=:subject_id")
        params["subject_id"] = subject_id
    _search(where, params, ("title",), q)
    predicate = " AND ".join(where)
    total = connection.execute(text(f"SELECT count(*) FROM public.flashcard_decks WHERE {predicate}"), params).scalar_one()
    rows = connection.execute(text(f"SELECT {DECK_FIELDS} FROM public.flashcard_decks WHERE {predicate} "
                                   "ORDER BY created_at DESC,id DESC LIMIT :limit OFFSET :offset"), params).mappings()
    return {"decks": [dict(row) for row in rows], "total": total}


def _card_filters(user_id, *, subject_id=None, topic_id=None, deck_id=None, resource_id=None, status="active"):
    params = {"user_id": user_id}
    where = ["user_id=:user_id"]
    for key, value in (("subject_id", subject_id), ("topic_id", topic_id), ("deck_id", deck_id), ("resource_id", resource_id)):
        if value is not None:
            where.append(f"{key}=:{key}")
            params[key] = value
    if status != "all":
        where.append("status=:status")
        params["status"] = status
    return where, params


def list_cards(connection, user_id, *, q=None, limit=50, offset=0, **filters):
    where, params = _card_filters(user_id, **filters)
    params.update(limit=limit, offset=offset)
    _search(where, params, ("front", "back"), q)
    predicate = " AND ".join(where)
    total = connection.execute(text(f"SELECT count(*) FROM public.flashcards WHERE {predicate}"), params).scalar_one()
    rows = connection.execute(text(f"SELECT {CARD_FIELDS} FROM public.flashcards WHERE {predicate} "
                                   "ORDER BY created_at DESC,id DESC LIMIT :limit OFFSET :offset"), params).mappings()
    return {"cards": [dict(row) for row in rows], "total": total}


def due_cards(connection, user_id, now, day_start, *, mode="due", subject_id=None, deck_id=None, limit=50, offset=0):
    where, params = _card_filters(user_id, subject_id=subject_id, deck_id=deck_id)
    params.update(now=now, day_start=day_start, limit=limit, offset=offset)
    predicate = " AND ".join(where)
    row = connection.execute(text("SELECT count(*) FILTER (WHERE next_review_at<:day_start) AS overdue,"
                                  "count(*) FILTER (WHERE next_review_at>=:day_start AND next_review_at<=:now) AS due_today,"
                                  f"count(*) FILTER (WHERE next_review_at>:now) AS upcoming FROM public.flashcards WHERE {predicate}"), params).mappings().one()
    summary = dict(row)
    condition = {"due": "next_review_at<=:now", "overdue": "next_review_at<:day_start",
                 "today": "next_review_at>=:day_start AND next_review_at<=:now", "upcoming": "next_review_at>:now"}[mode]
    rows = connection.execute(text(f"SELECT {CARD_FIELDS} FROM public.flashcards WHERE {predicate} AND {condition} "
                                   "ORDER BY next_review_at,id LIMIT :limit OFFSET :offset"), params).mappings()
    total = summary["overdue"] + summary["due_today"] if mode == "due" else summary["due_today" if mode == "today" else mode]
    return {"cards": [dict(card) for card in rows], "total": total, "summary": summary}


def review_by_request(connection, user_id, request_id):
    row = connection.execute(text(f"SELECT {REVIEW_FIELDS} FROM public.flashcard_reviews WHERE user_id=:user_id AND request_id=:request_id"),
                             {"user_id": user_id, "request_id": request_id}).mappings().first()
    return dict(row) if row else None


def insert_review(connection, user_id, data):
    allowed = set(REVIEW_FIELDS.split(",")) - {"id", "created_at"}
    values = {key: value for key, value in data.items() if key in allowed}
    values["user_id"] = user_id
    columns = ",".join(values)
    placeholders = ",".join(f":{key}" for key in values)
    row = connection.execute(text(f"INSERT INTO public.flashcard_reviews({columns}) VALUES ({placeholders}) RETURNING {REVIEW_FIELDS}"), values).mappings().one()
    return dict(row)


def apply_review(connection, user_id, card_id, interval_days, next_review_at):
    connection.execute(text("UPDATE public.flashcards SET interval_days=:interval,next_review_at=:due,review_revision=review_revision+1 "
                            "WHERE user_id=:user_id AND id=:id"), {"user_id": user_id, "id": card_id, "interval": interval_days, "due": next_review_at})


def list_reviews(connection, user_id, card_id, *, limit=50, offset=0):
    params = {"user_id": user_id, "id": card_id, "limit": limit, "offset": offset}
    predicate = "user_id=:user_id AND flashcard_id=:id"
    total = connection.execute(text(f"SELECT count(*) FROM public.flashcard_reviews WHERE {predicate}"), params).scalar_one()
    rows = connection.execute(text(f"SELECT {REVIEW_FIELDS} FROM public.flashcard_reviews WHERE {predicate} "
                                   "ORDER BY reviewed_at DESC,id DESC LIMIT :limit OFFSET :offset"), params).mappings()
    return {"reviews": [dict(row) for row in rows], "total": total}
