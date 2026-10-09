"""Bounded owner-scoped assessment SQL and coherent component counts."""
from contextlib import contextmanager

from sqlalchemy import bindparam, text

from app.db.connection import get_engine
from app.repositories.planner import profile_timezone

ASSESSMENT_FIELDS = "id,title,description,scheduled_at,status,created_at,updated_at"
ATTEMPT_FIELDS = "id,assessment_id,started_at,completed_at,score,max_score,percentage,notes,created_at,updated_at"


@contextmanager
def transaction(*, readonly=False):
    if readonly:
        with get_engine().connect().execution_options(isolation_level="REPEATABLE READ") as connection:
            with connection.begin():
                connection.execute(text("SET TRANSACTION READ ONLY"))
                yield connection
    else:
        with get_engine().begin() as connection:
            yield connection


def _in(statement, key):
    return text(statement).bindparams(bindparam(key, expanding=True))


def valid_coverage(connection, topic_ids, subject_ids):
    subjects = list(connection.execute(_in("SELECT id FROM public.subjects WHERE is_active AND id IN :ids ORDER BY id FOR SHARE", "ids"),
                                       {"ids": subject_ids}).scalars()) if subject_ids else []
    if len(subjects) != len(subject_ids):
        return False
    topics = list(connection.execute(_in("SELECT t.id,t.subject_id FROM public.topics t JOIN public.subjects s ON s.id=t.subject_id "
                                         "WHERE s.is_active AND t.id IN :ids ORDER BY t.id FOR SHARE OF t,s", "ids"),
                                     {"ids": topic_ids}).mappings()) if topic_ids else []
    return len(topics) == len(topic_ids) and all(row["subject_id"] not in set(subject_ids) for row in topics)


def _with_coverage(connection, user_id, rows):
    if not rows:
        return rows
    by_id = {row["id"]: {**row, "topic_ids": [], "subject_ids": [], "coverage_topics": [], "coverage_subjects": [], "topic_count": 0} for row in rows}
    params = {"user_id": user_id, "ids": list(by_id)}
    for kind, column in (("topics", "topic_id"), ("subjects", "subject_id")):
        statement = _in(f"SELECT assessment_id,{column} FROM public.assessment_{kind} "
                        "WHERE user_id=:user_id AND assessment_id IN :ids ORDER BY assessment_id,display_order", "ids")
        for row in connection.execute(statement, params).mappings():
            by_id[row["assessment_id"]]["topic_ids" if kind == "topics" else "subject_ids"].append(row[column])
    statement = _in("SELECT e.assessment_id,t.id,t.subject_id,t.code,t.title FROM public.assessment_topics e JOIN public.topics t ON t.id=e.topic_id "
                    "JOIN public.subjects s ON s.id=t.subject_id WHERE e.user_id=:user_id AND e.assessment_id IN :ids "
                    "ORDER BY e.assessment_id,s.display_order,t.display_order,t.id", "ids")
    for row in connection.execute(statement, params).mappings():
        by_id[row["assessment_id"]]["coverage_topics"].append({key: row[key] for key in ("id", "subject_id", "code", "title")})
    statement = _in("WITH covered AS (SELECT assessment_id,subject_id,true AS whole FROM public.assessment_subjects "
                    "WHERE user_id=:user_id AND assessment_id IN :ids UNION ALL "
                    "SELECT a.assessment_id,t.subject_id,false FROM public.assessment_topics a JOIN public.topics t ON t.id=a.topic_id "
                    "WHERE a.user_id=:user_id AND a.assessment_id IN :ids) "
                    "SELECT c.assessment_id,s.id,s.code,s.name,bool_or(c.whole) AS whole FROM covered c JOIN public.subjects s ON s.id=c.subject_id "
                    "GROUP BY c.assessment_id,s.id ORDER BY c.assessment_id,s.display_order,s.id", "ids")
    for row in connection.execute(statement, params).mappings():
        by_id[row["assessment_id"]]["coverage_subjects"].append({"id": row["id"], "code": row["code"], "name": row["name"],
                                                                "scope": "all_topics" if row["whole"] else "selected_topics"})
    # Counts include whole subjects without returning all their topic rows.
    statement = _in("WITH effective AS (SELECT assessment_id,topic_id FROM public.assessment_topics "
                    "WHERE user_id=:user_id AND assessment_id IN :ids UNION "
                    "SELECT a.assessment_id,t.id FROM public.assessment_subjects a JOIN public.topics t ON t.subject_id=a.subject_id "
                    "WHERE a.user_id=:user_id AND a.assessment_id IN :ids) "
                    "SELECT assessment_id,count(*) AS topic_count FROM effective GROUP BY assessment_id", "ids")
    for row in connection.execute(statement, params).mappings():
        by_id[row["assessment_id"]]["topic_count"] = row["topic_count"]
    return list(by_id.values())


def get_assessment(connection, user_id, assessment_id, *, lock=False):
    row = connection.execute(text(f"SELECT {ASSESSMENT_FIELDS} FROM public.assessments WHERE user_id=:user_id AND id=:id" +
                                  (" FOR UPDATE" if lock else "")), {"user_id": user_id, "id": assessment_id}).mappings().first()
    return _with_coverage(connection, user_id, [dict(row)])[0] if row else None


def list_assessments(connection, user_id, *, status="all", q=None, limit=50, offset=0):
    where = ["user_id=:user_id"]
    params = {"user_id": user_id, "limit": limit, "offset": offset}
    if status == "all":
        where.append("status<>'archived'")
    else:
        where.append("status=:status")
        params["status"] = status
    if q:
        where.append("title ILIKE :q ESCAPE '\\'")
        params["q"] = "%" + q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
    predicate = " AND ".join(where)
    total = connection.execute(text(f"SELECT count(*) FROM public.assessments WHERE {predicate}"), params).scalar_one()
    rows = [dict(row) for row in connection.execute(text(f"SELECT {ASSESSMENT_FIELDS} FROM public.assessments WHERE {predicate} "
                                                       "ORDER BY scheduled_at NULLS LAST,created_at,id LIMIT :limit OFFSET :offset"), params).mappings()]
    return {"assessments": _with_coverage(connection, user_id, rows), "total": total}


def write_assessment(connection, user_id, data, assessment_id=None):
    values = data.model_dump(exclude={"topic_ids", "subject_ids"})
    if assessment_id is None:
        values["user_id"] = user_id
        columns = ",".join(values)
        placeholders = ",".join(f":{key}" for key in values)
        assessment_id = connection.execute(text(f"INSERT INTO public.assessments({columns}) VALUES ({placeholders}) RETURNING id"), values).scalar_one()
    else:
        setters = ",".join(f"{key}=:{key}" for key in values)
        connection.execute(text(f"UPDATE public.assessments SET {setters} WHERE user_id=:user_id AND id=:id"),
                           {**values, "user_id": user_id, "id": assessment_id})
    for kind, column, ids in (("topics", "topic_id", data.topic_ids), ("subjects", "subject_id", data.subject_ids)):
        connection.execute(text(f"DELETE FROM public.assessment_{kind} WHERE user_id=:user_id AND assessment_id=:id"),
                           {"user_id": user_id, "id": assessment_id})
        if ids:
            connection.execute(text(f"INSERT INTO public.assessment_{kind}(user_id,assessment_id,{column},display_order) "
                                    "VALUES (:user_id,:assessment_id,:coverage_id,:display_order)"),
                               [{"user_id": user_id, "assessment_id": assessment_id, "coverage_id": value, "display_order": index} for index, value in enumerate(ids)])
    return get_assessment(connection, user_id, assessment_id)


def archive_assessment(connection, user_id, assessment_id):
    connection.execute(text("UPDATE public.assessments SET status='archived' WHERE user_id=:user_id AND id=:id AND status<>'archived'"),
                       {"user_id": user_id, "id": assessment_id})


def get_attempt(connection, user_id, attempt_id, *, lock=False):
    row = connection.execute(text(f"SELECT {ATTEMPT_FIELDS} FROM public.assessment_attempts WHERE user_id=:user_id AND id=:id" +
                                  (" FOR UPDATE" if lock else "")), {"user_id": user_id, "id": attempt_id}).mappings().first()
    return dict(row) if row else None


def write_attempt(connection, user_id, assessment_id, data, attempt_id=None):
    allowed = {"started_at", "completed_at", "score", "max_score", "percentage", "notes"}
    values = {key: value for key, value in data.items() if key in allowed}
    if attempt_id is None:
        values.update(user_id=user_id, assessment_id=assessment_id)
        columns = ",".join(values)
        placeholders = ",".join(f":{key}" for key in values)
        row = connection.execute(text(f"INSERT INTO public.assessment_attempts({columns}) VALUES ({placeholders}) RETURNING {ATTEMPT_FIELDS}"), values).mappings().one()
    else:
        setters = ",".join(f"{key}=:{key}" for key in values)
        row = connection.execute(text(f"UPDATE public.assessment_attempts SET {setters} WHERE user_id=:user_id AND id=:id RETURNING {ATTEMPT_FIELDS}"),
                                 {**values, "user_id": user_id, "id": attempt_id}).mappings().one()
    return dict(row)


def list_attempts(connection, user_id, assessment_id, *, limit=50, offset=0):
    params = {"user_id": user_id, "id": assessment_id, "limit": limit, "offset": offset}
    predicate = "user_id=:user_id AND assessment_id=:id"
    total = connection.execute(text(f"SELECT count(*) FROM public.assessment_attempts WHERE {predicate}"), params).scalar_one()
    rows = connection.execute(text(f"SELECT {ATTEMPT_FIELDS} FROM public.assessment_attempts WHERE {predicate} "
                                   "ORDER BY created_at DESC,id DESC LIMIT :limit OFFSET :offset"), params).mappings()
    return {"attempts": [dict(row) for row in rows], "total": total}


def readiness_counts(connection, user_id, assessment_id, now, day_start):
    # Quiz denominator is frozen covered questions in each completed attempt,
    # including unanswered questions; live question edits cannot alter coverage.
    statement = text("""
        WITH whole_subjects AS (
            SELECT subject_id FROM public.assessment_subjects WHERE user_id=:user_id AND assessment_id=:id
        ), effective_topics AS (
            SELECT topic_id FROM public.assessment_topics WHERE user_id=:user_id AND assessment_id=:id
            UNION SELECT t.id FROM public.topics t JOIN whole_subjects s ON s.subject_id=t.subject_id
        ), video_counts AS (
            SELECT count(*) AS total_videos,count(*) FILTER (WHERE p.status='completed') AS completed_videos
            FROM public.videos v JOIN effective_topics t ON t.topic_id=v.topic_id
            LEFT JOIN public.user_video_progress p ON p.video_id=v.id AND p.user_id=:user_id
        ), quiz_counts AS (
            SELECT count(*) AS quiz_graded_answers,count(*) FILTER (WHERE a.is_correct IS TRUE) AS quiz_correct_answers
            FROM public.quiz_attempts qa CROSS JOIN LATERAL jsonb_array_elements(qa.snapshot) q
            JOIN effective_topics t ON t.topic_id::text=q->>'topic_id'
            LEFT JOIN public.quiz_answers a ON a.attempt_id=qa.id AND a.user_id=:user_id AND a.question_id::text=q->>'id'
            WHERE qa.user_id=:user_id AND qa.status='completed' AND qa.completed_at IS NOT NULL
        ), card_counts AS (
            SELECT count(*) AS active_flashcards,
                count(*) FILTER (WHERE EXISTS (SELECT 1 FROM public.flashcard_reviews r WHERE r.user_id=:user_id AND r.flashcard_id=f.id)) AS reviewed_flashcards,
                count(*) FILTER (WHERE f.next_review_at<=:now) AS due_flashcards,
                count(*) FILTER (WHERE f.next_review_at<:day_start) AS overdue_flashcards
            FROM public.flashcards f WHERE f.user_id=:user_id AND f.status='active'
                AND (f.topic_id IN (SELECT topic_id FROM effective_topics) OR f.subject_id IN (SELECT subject_id FROM whole_subjects))
        ) SELECT (SELECT count(*) FROM effective_topics) AS topic_count,video_counts.*,quiz_counts.*,card_counts.*
            FROM video_counts CROSS JOIN quiz_counts CROSS JOIN card_counts
    """)
    return dict(connection.execute(statement, {"user_id": user_id, "id": assessment_id, "now": now, "day_start": day_start}).mappings().one())
