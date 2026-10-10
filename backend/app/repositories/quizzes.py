"""Owner-bound quiz SQL; all table/column interpolation is fixed application code."""
import hashlib
import json
from contextlib import contextmanager
from uuid import uuid4

from sqlalchemy import bindparam, text

from app.db.connection import get_engine
from app.repositories.planner import valid_associations
from app.schemas.quizzes import QuestionInput

QUESTION_FIELDS = "id,subject_id,topic_id,resource_id,source_page,question_type,prompt,explanation,origin,ai_provenance,is_archived,created_at,updated_at"
QUIZ_FIELDS = "q.id,q.title,q.description,q.subject_id,q.topic_id,q.is_archived,q.created_at,q.updated_at"
QUIZ_DERIVED = "(SELECT count(*) FROM public.quiz_questions qq WHERE qq.quiz_id=q.id AND qq.user_id=q.user_id) AS question_count,(SELECT a.id FROM public.quiz_attempts a WHERE a.quiz_id=q.id AND a.user_id=q.user_id AND a.status='in_progress') AS active_attempt_id"
ATTEMPT_FIELDS = "id,quiz_id,title,status,started_at,completed_at,score_value,total_questions,score_percent"


@contextmanager
def transaction():
    with get_engine().begin() as connection:
        yield connection


def question_hashes(data):
    payload = data.model_dump(mode="json", exclude={"ai_draft_receipt", "ai_provenance"})
    payload["prompt"] = " ".join(payload["prompt"].split())
    identity = {key: payload[key] for key in ("subject_id", "topic_id", "prompt")}
    # Option/key ordering is presentation only for duplicate detection.
    payload["options"] = sorted(payload["options"], key=lambda o: o["key"])
    payload["correct_keys"] = sorted(payload["correct_keys"])
    digest = lambda value: hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    return digest(identity), digest(payload)


def lock_import_owner(connection, user_id):
    connection.execute(text("SELECT id FROM public.profiles WHERE id=:user_id FOR UPDATE"), {"user_id": user_id}).scalar_one()


def import_catalog(connection):
    subjects = connection.execute(text("SELECT id,code FROM public.subjects WHERE is_active ORDER BY display_order,id")).mappings()
    topics = connection.execute(text("SELECT t.id,t.subject_id,t.code FROM public.topics t JOIN public.subjects s ON s.id=t.subject_id WHERE s.is_active")).mappings()
    return {"subjects": [dict(row) for row in subjects], "topics": [dict(row) for row in topics]}


def find_import_question(connection, user_id, identity_hash):
    row = connection.execute(text("SELECT id,identity_hash,content_hash FROM public.questions WHERE user_id=:user_id AND identity_hash=:identity_hash"),
                             {"user_id": user_id, "identity_hash": identity_hash}).mappings().first()
    if row is None:
        return None
    question = get_question(connection, user_id, row["id"])
    # Source deletion can detach associations through the database trigger.
    # Derive the current fingerprint rather than trusting its old stored value.
    data = QuestionInput.model_validate({key: question[key] for key in QuestionInput.model_fields if key in question})
    identity_hash, content_hash = question_hashes(data)
    return {**question, "identity_hash": identity_hash, "content_hash": content_hash}


def find_import_questions(connection, user_id, identity_hashes):
    if not identity_hashes:
        return {}
    query = text(f"SELECT {QUESTION_FIELDS},identity_hash FROM public.questions "
                 "WHERE user_id=:user_id AND identity_hash IN :identity_hashes ORDER BY id")
    query = query.bindparams(bindparam("identity_hashes", expanding=True))
    rows = connection.execute(query, {"user_id": user_id, "identity_hashes": sorted(set(identity_hashes))}).mappings().all()
    existing = {}
    for row in attach_question_options(connection, user_id, rows):
        data = QuestionInput.model_validate({key: row[key] for key in QuestionInput.model_fields if key in row})
        _, content_hash = question_hashes(data)
        existing[row["identity_hash"]] = {**row, "content_hash": content_hash}
    return existing


def question_options(connection, user_id, question_id):
    rows = connection.execute(text("SELECT option_key,text,is_correct FROM public.question_options WHERE user_id=:user_id AND question_id=:id ORDER BY display_order"),
                              {"user_id": user_id, "id": question_id}).mappings().all()
    return {"options": [{"key": r["option_key"], "text": r["text"]} for r in rows], "correct_keys": [r["option_key"] for r in rows if r["is_correct"]]}


def get_question(connection, user_id, question_id, *, lock=False):
    row = connection.execute(text(f"SELECT {QUESTION_FIELDS} FROM public.questions WHERE user_id=:user_id AND id=:id" + (" FOR SHARE" if lock else "")),
                             {"user_id": user_id, "id": question_id}).mappings().first()
    return {**dict(row), **question_options(connection, user_id, question_id)} if row else None


def attach_question_options(connection, user_id, questions):
    if not questions:
        return []
    ids = sorted(row["id"] for row in questions)
    query = text("SELECT question_id,option_key,text,is_correct FROM public.question_options "
                 "WHERE user_id=:user_id AND question_id IN :question_ids ORDER BY question_id,display_order")
    query = query.bindparams(bindparam("question_ids", expanding=True))
    rows = connection.execute(query, {"user_id": user_id, "question_ids": ids}).mappings().all()
    options = {qid: {"options": [], "correct_keys": []} for qid in ids}
    for row in rows:
        item = options[row["question_id"]]
        item["options"].append({"key": row["option_key"], "text": row["text"]})
        if row["is_correct"]:
            item["correct_keys"].append(row["option_key"])
    return [{**dict(row), **options[row["id"]]} for row in questions]


def get_questions(connection, user_id, question_ids, *, lock=False):
    if not question_ids:
        return {}
    query = text(f"SELECT {QUESTION_FIELDS} FROM public.questions WHERE user_id=:user_id "
                 "AND id IN :question_ids ORDER BY id" + (" FOR SHARE" if lock else ""))
    query = query.bindparams(bindparam("question_ids", expanding=True))
    rows = connection.execute(query, {"user_id": user_id, "question_ids": sorted(set(question_ids))}).mappings().all()
    return {row["id"]: row for row in attach_question_options(connection, user_id, rows)}


def _search(params, where, alias, q):
    if q:
        where.append(f"{alias} ILIKE :q ESCAPE '\\'")
        params["q"] = "%" + q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"


def list_questions(connection, user_id, *, subject_id=None, topic_id=None, resource_id=None, question_type=None, q=None, limit=50, offset=0):
    params = {"user_id": user_id, "limit": limit, "offset": offset}
    where = ["user_id=:user_id", "NOT is_archived"]
    for key, value in (("subject_id", subject_id), ("topic_id", topic_id), ("resource_id", resource_id), ("question_type", question_type)):
        if value is not None:
            where.append(f"{key}=:{key}")
            params[key] = value
    _search(params, where, "prompt", q)
    predicate = " AND ".join(where)
    total = connection.execute(text(f"SELECT count(*) FROM public.questions WHERE {predicate}"), params).scalar_one()
    rows = connection.execute(text(f"SELECT {QUESTION_FIELDS} FROM public.questions WHERE {predicate} ORDER BY created_at DESC,id DESC LIMIT :limit OFFSET :offset"), params).mappings().all()
    return {"questions": attach_question_options(connection, user_id, rows), "total": total}


def _write_options(connection, user_id, question_id, data):
    connection.execute(text("INSERT INTO public.question_options(user_id,question_id,option_key,text,is_correct,display_order) VALUES (:user_id,:question_id,:key,:text,:is_correct,:display_order)"),
                       [{"user_id": user_id, "question_id": question_id, "key": option.key, "text": option.text,
                         "is_correct": option.key in data.correct_keys, "display_order": index} for index, option in enumerate(data.options)])


def insert_question(connection, user_id, data, *, origin="manual", identity_hash=None, content_hash=None, ai_provenance=None):
    identity_hash, content_hash = question_hashes(data) if identity_hash is None or content_hash is None else (identity_hash, content_hash)
    values = data.model_dump(exclude={"options", "correct_keys"})
    values.update(user_id=user_id, origin=origin, identity_hash=identity_hash, content_hash=content_hash)
    if ai_provenance is not None:
        values["ai_provenance"] = json.dumps(ai_provenance)
    columns = ",".join(values)
    placeholders = ",".join("CAST(:ai_provenance AS jsonb)" if key == "ai_provenance" else f":{key}" for key in values)
    question_id = connection.execute(text(f"INSERT INTO public.questions({columns}) VALUES ({placeholders}) RETURNING id"), values).scalar_one()
    _write_options(connection, user_id, question_id, data)
    return get_question(connection, user_id, question_id)


def insert_questions(connection, user_id, entries, *, origin="csv"):
    if not entries:
        return
    questions = []
    options = []
    for data, identity_hash, content_hash in entries:
        question_id = uuid4()
        values = data.model_dump(exclude={"options", "correct_keys"})
        questions.append({**values, "id": question_id, "user_id": user_id, "origin": origin,
                          "identity_hash": identity_hash, "content_hash": content_hash})
        options.extend({"user_id": user_id, "question_id": question_id, "key": option.key, "text": option.text,
                        "is_correct": option.key in data.correct_keys, "display_order": index}
                       for index, option in enumerate(data.options))
    columns = ",".join(questions[0])
    placeholders = ",".join(f":{key}" for key in questions[0])
    connection.execute(text(f"INSERT INTO public.questions({columns}) VALUES ({placeholders})"), questions)
    connection.execute(text("INSERT INTO public.question_options(user_id,question_id,option_key,text,is_correct,display_order) "
                            "VALUES (:user_id,:question_id,:key,:text,:is_correct,:display_order)"), options)


def update_question(connection, user_id, question_id, data, *, ai_provenance=None):
    values = data.model_dump(exclude={"options", "correct_keys"})
    values["identity_hash"], values["content_hash"] = question_hashes(data)
    if ai_provenance is not None:
        values.update(origin="ai", ai_provenance=json.dumps(ai_provenance))
    setters = ",".join("ai_provenance=CAST(:ai_provenance AS jsonb)" if key == "ai_provenance" else f"{key}=:{key}" for key in values)
    connection.execute(text(f"UPDATE public.questions SET {setters} WHERE user_id=:user_id AND id=:id"), {**values, "user_id": user_id, "id": question_id})
    connection.execute(text("DELETE FROM public.question_options WHERE user_id=:user_id AND question_id=:id"), {"user_id": user_id, "id": question_id})
    _write_options(connection, user_id, question_id, data)
    return get_question(connection, user_id, question_id)


def lock_question(connection, user_id, question_id):
    return connection.execute(text("SELECT id FROM public.questions WHERE user_id=:user_id AND id=:id FOR UPDATE"), {"user_id": user_id, "id": question_id}).first()


def valid_resource(connection, user_id, resource_id, source_page):
    if resource_id is None:
        return source_page is None
    row = connection.execute(text("SELECT resource_type,page_count FROM public.resources WHERE user_id=:user_id AND id=:id FOR SHARE"),
                             {"user_id": user_id, "id": resource_id}).mappings().first()
    return row is not None and (source_page is None or (row["resource_type"] == "pdf" and row["page_count"] is not None and source_page <= row["page_count"]))


def archive(connection, kind, user_id, record_id):
    table = {"question": "questions", "quiz": "quizzes"}[kind]
    connection.execute(text(f"UPDATE public.{table} SET is_archived=true WHERE user_id=:user_id AND id=:id"), {"user_id": user_id, "id": record_id})


def get_quiz(connection, user_id, quiz_id, *, lock=False):
    row = connection.execute(text(f"SELECT {QUIZ_FIELDS},{QUIZ_DERIVED} FROM public.quizzes q WHERE q.user_id=:user_id AND q.id=:id" + (" FOR UPDATE OF q" if lock else "")),
                             {"user_id": user_id, "id": quiz_id}).mappings().first()
    return dict(row) if row else None


def quiz_question_ids(connection, user_id, quiz_id):
    return list(connection.execute(text("SELECT question_id FROM public.quiz_questions WHERE user_id=:user_id AND quiz_id=:id ORDER BY display_order"), {"user_id": user_id, "id": quiz_id}).scalars())


def list_quizzes(connection, user_id, *, subject_id=None, q=None, limit=50, offset=0):
    params = {"user_id": user_id, "limit": limit, "offset": offset}
    where = ["q.user_id=:user_id", "NOT q.is_archived"]
    if subject_id is not None:
        where.append("q.subject_id=:subject_id")
        params["subject_id"] = subject_id
    _search(params, where, "q.title", q)
    predicate = " AND ".join(where)
    total = connection.execute(text(f"SELECT count(*) FROM public.quizzes q WHERE {predicate}"), params).scalar_one()
    rows = connection.execute(text(f"SELECT {QUIZ_FIELDS},{QUIZ_DERIVED} FROM public.quizzes q WHERE {predicate} ORDER BY q.created_at DESC,q.id DESC LIMIT :limit OFFSET :offset"), params).mappings()
    return {"quizzes": [dict(r) for r in rows], "total": total}


def write_quiz(connection, user_id, data, quiz_id=None):
    values = data.model_dump(exclude={"question_ids"})
    if quiz_id is None:
        values["user_id"] = user_id
        columns = ",".join(values)
        placeholders = ",".join(f":{key}" for key in values)
        quiz_id = connection.execute(text(f"INSERT INTO public.quizzes({columns}) VALUES ({placeholders}) RETURNING id"), values).scalar_one()
    else:
        setters = ",".join(f"{key}=:{key}" for key in values)
        connection.execute(text(f"UPDATE public.quizzes SET {setters} WHERE user_id=:user_id AND id=:id"), {**values, "user_id": user_id, "id": quiz_id})
        connection.execute(text("DELETE FROM public.quiz_questions WHERE user_id=:user_id AND quiz_id=:id"), {"user_id": user_id, "id": quiz_id})
    connection.execute(text("INSERT INTO public.quiz_questions(user_id,quiz_id,question_id,display_order) VALUES (:user_id,:quiz_id,:question_id,:display_order)"),
                       [{"user_id": user_id, "quiz_id": quiz_id, "question_id": qid, "display_order": index} for index, qid in enumerate(data.question_ids)])
    return get_quiz(connection, user_id, quiz_id)


def get_attempt(connection, user_id, attempt_id, *, lock=False):
    row = connection.execute(text(f"SELECT {ATTEMPT_FIELDS},snapshot FROM public.quiz_attempts WHERE user_id=:user_id AND id=:id" + (" FOR UPDATE" if lock else "")), {"user_id": user_id, "id": attempt_id}).mappings().first()
    return dict(row) if row else None


def active_attempt(connection, user_id, quiz_id):
    return connection.execute(text("SELECT id FROM public.quiz_attempts WHERE user_id=:user_id AND quiz_id=:id AND status='in_progress'"), {"user_id": user_id, "id": quiz_id}).scalar_one_or_none()


def insert_attempt(connection, user_id, quiz, snapshot):
    attempt_id = connection.execute(text("INSERT INTO public.quiz_attempts(user_id,quiz_id,title,snapshot,total_questions) VALUES (:user_id,:quiz_id,:title,CAST(:snapshot AS jsonb),:total) RETURNING id"),
                                    {"user_id": user_id, "quiz_id": quiz["id"], "title": quiz["title"], "snapshot": json.dumps(snapshot), "total": len(snapshot)}).scalar_one()
    return get_attempt(connection, user_id, attempt_id)


def answers(connection, user_id, attempt_id):
    rows = connection.execute(text("SELECT question_id,selected_keys,is_correct FROM public.quiz_answers WHERE user_id=:user_id AND attempt_id=:id"), {"user_id": user_id, "id": attempt_id}).mappings()
    return {str(r["question_id"]): {"selected_keys": r["selected_keys"], "is_correct": r["is_correct"]} for r in rows}


def save_answer(connection, user_id, attempt_id, question_id, selected_keys, *, is_correct=None):
    connection.execute(text("INSERT INTO public.quiz_answers(user_id,attempt_id,question_id,selected_keys,is_correct) VALUES (:user_id,:attempt_id,:question_id,CAST(:selected_keys AS jsonb),:is_correct) ON CONFLICT(attempt_id,question_id) DO UPDATE SET selected_keys=EXCLUDED.selected_keys,is_correct=EXCLUDED.is_correct,answered_at=now() WHERE public.quiz_answers.user_id=:user_id"),
                       {"user_id": user_id, "attempt_id": attempt_id, "question_id": question_id, "selected_keys": json.dumps(selected_keys), "is_correct": is_correct})


def finish_attempt(connection, user_id, attempt_id, score, percent):
    connection.execute(text("UPDATE public.quiz_attempts SET status='completed',completed_at=now(),score_value=:score,score_percent=:percent WHERE user_id=:user_id AND id=:id AND status='in_progress'"), {"user_id": user_id, "id": attempt_id, "score": score, "percent": percent})
    return get_attempt(connection, user_id, attempt_id)


def list_attempts(connection, user_id, *, quiz_id=None, limit=50, offset=0):
    params = {"user_id": user_id, "limit": limit, "offset": offset}
    predicate = "user_id=:user_id"
    if quiz_id is not None:
        predicate += " AND quiz_id=:quiz_id"
        params["quiz_id"] = quiz_id
    total = connection.execute(text(f"SELECT count(*) FROM public.quiz_attempts WHERE {predicate}"), params).scalar_one()
    rows = connection.execute(text(f"SELECT {ATTEMPT_FIELDS} FROM public.quiz_attempts WHERE {predicate} ORDER BY started_at DESC,id DESC LIMIT :limit OFFSET :offset"), params).mappings()
    return {"attempts": [dict(r) for r in rows], "total": total}
