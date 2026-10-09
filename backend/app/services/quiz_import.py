"""Read-only question previews and transactional, reviewed CSV insertions."""
import base64
import binascii
import hashlib
import hmac
import json
import time

from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.core.config import get_settings
from app.parsers.quiz_csv_parser import QuizImportError, issue, parse_quiz_csv
from app.repositories import quizzes as repo
from app.schemas.quizzes import QuestionInput
from app.services import quizzes as quiz_service

TOKEN_LIFETIME = 15 * 60
TOKEN_PURPOSE = b"study-hub/question-csv-preview/v1:"


def _secret(secret):
    value = secret if secret is not None else get_settings().supabase_secret_key.get_secret_value()
    if not value:
        raise QuizImportError(503, "Question import confirmation is unavailable. Try again.")
    return value.encode("utf-8")


def _encoded(value):
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def create_preview_token(user_id, data, *, secret=None, now=None):
    stamp = int(time.time() if now is None else now)
    payload = json.dumps({"user": str(user_id), "file": hashlib.sha256(data).hexdigest(),
                          "exp": stamp + TOKEN_LIFETIME}, sort_keys=True, separators=(",", ":")).encode("utf-8")
    encoded = _encoded(payload)
    signature = hmac.new(_secret(secret), TOKEN_PURPOSE + encoded.encode("ascii"), hashlib.sha256).digest()
    return encoded + "." + _encoded(signature)


def verify_preview_token(token, user_id, data, *, secret=None, now=None):
    key = _secret(secret)
    try:
        if not isinstance(token, str) or len(token) > 2048:
            raise ValueError
        encoded, signature = token.split(".")
        expected = _encoded(hmac.new(key, TOKEN_PURPOSE + encoded.encode("ascii"), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            raise ValueError
        payload = json.loads(base64.b64decode(encoded + "=" * (-len(encoded) % 4), altchars=b"-_", validate=True))
        stamp = int(time.time() if now is None else now)
        if (set(payload) != {"user", "file", "exp"} or type(payload["exp"]) is not int or
                payload["exp"] <= stamp or payload["exp"] > stamp + TOKEN_LIFETIME or
                payload["user"] != str(user_id) or payload["file"] != hashlib.sha256(data).hexdigest()):
            raise ValueError
    except (ValueError, TypeError, UnicodeError, binascii.Error):
        raise QuizImportError(422, "Import preview confirmation is invalid or expired. Preview this file again.") from None


def _question(row_number, values, catalog):
    values = {key: value.strip() for key, value in values.items()}
    errors = []
    subject_code = values.get("subject", "")
    if subject_code == "MS":
        subject_code = "MAS"
    subject_id = None
    topic_id = None
    if subject_code:
        matches = [subject for subject in catalog["subjects"] if subject["code"] == subject_code]
        if len(matches) != 1:
            errors.append(issue(row_number, "subject", "Subject code must match one active subject."))
        else:
            subject_id = matches[0]["id"]
    topic_code = values.get("topic", "")
    if topic_code:
        matches = [topic for topic in catalog["topics"] if topic["code"] == topic_code and topic["subject_id"] == subject_id]
        if subject_id is None or len(matches) != 1:
            errors.append(issue(row_number, "topic", "Topic code must uniquely match a topic under the selected subject."))
        else:
            topic_id = matches[0]["id"]
    kind = values.get("question_type") or "single_select"
    options = [{"key": letter, "text": values.get("option_" + letter.lower(), "")} for letter in "ABCDEF"
               if values.get("option_" + letter.lower(), "")]
    if kind == "true_false":
        if options:
            errors.append(issue(row_number, "options", "True/false rows require blank option fields."))
        options = [{"key": "TRUE", "text": "True"}, {"key": "FALSE", "text": "False"}]
    correct_keys = values.get("correct_answer", "").split(";")
    correct_keys = sorted(key.strip().upper() for key in correct_keys)
    page = values.get("source_page", "")
    if page and (len(page) > 3 or not page.isascii() or not page.isdecimal() or not 1 <= int(page) <= 200):
        errors.append(issue(row_number, "source_page", "Source page must be a positive integer of at most 200."))
    if errors:
        return None, errors
    try:
        question = QuestionInput.model_validate({"subject_id": subject_id, "topic_id": topic_id,
            "resource_id": values.get("resource_id") or None, "source_page": int(page) if page else None,
            "question_type": kind, "prompt": " ".join(values.get("question", "").split()),
            "explanation": values.get("explanation") or None, "options": options, "correct_keys": correct_keys})
    except ValidationError as error:
        for detail in error.errors(include_input=False, include_context=False):
            field = str(detail["loc"][0]) if detail["loc"] else "row"
            field = {"prompt": "question", "correct_keys": "correct_answer"}.get(field, field)
            errors.append(issue(row_number, field, "Invalid question value: " + detail["msg"]))
        return None, errors
    return question, []


def build_preview(connection, user_id, data):
    parsed = parse_quiz_csv(data)
    report = {"row_count": parsed.row_count, "valid_count": 0, "duplicate_count": 0,
              "proposed_inserts": 0, "unchanged": 0, "warnings": [], "errors": list(parsed.errors),
              "sample": [], "preview_token": None}
    inserts = []
    if parsed.errors:
        return report, inserts
    catalog = repo.import_catalog(connection)
    seen = {}
    candidates = []
    associations = {}
    for row_number, values in parsed.rows:
        question, errors = _question(row_number, values, catalog)
        report["errors"].extend(errors)
        if question is None:
            continue
        association = (question.subject_id, question.topic_id, question.resource_id, question.source_page)
        if association not in associations:
            try:
                quiz_service.validate_question_associations(connection, user_id, question)
                associations[association] = None
            except quiz_service.QuizError as error:
                associations[association] = error.detail
        if associations[association] is not None:
            report["errors"].append(issue(row_number, "resource_id" if question.resource_id else "topic", associations[association]))
            continue
        report["valid_count"] += 1
        identity_hash, content_hash = repo.question_hashes(question)
        if identity_hash in seen:
            if seen[identity_hash] == content_hash:
                report["duplicate_count"] += 1
                report["unchanged"] += 1
                report["warnings"].append(issue(row_number, "question", "Exact duplicate in this CSV; skipped."))
            else:
                report["errors"].append(issue(row_number, "question", "Question identity conflicts with different content in this CSV."))
            continue
        seen[identity_hash] = content_hash
        candidates.append((row_number, question, identity_hash, content_hash))
    # The transaction retains association locks. Commit rebuilds this preview
    # after its owner lock, so edits/imports cannot race the duplicate check.
    existing_questions = repo.find_import_questions(connection, user_id, list(seen))
    for row_number, question, identity_hash, content_hash in candidates:
        existing = existing_questions.get(identity_hash)
        if existing:
            if existing["content_hash"] == content_hash:
                report["duplicate_count"] += 1
                report["unchanged"] += 1
                report["warnings"].append(issue(row_number, "question", "Exact existing question; unchanged."))
            else:
                report["errors"].append(issue(row_number, "question", "An existing question has this identity with different content."))
            continue
        inserts.append((question, identity_hash, content_hash))
        if len(report["sample"]) < 20:
            report["sample"].append(question.model_dump(mode="json"))
    report["proposed_inserts"] = len(inserts)
    return report, inserts


def preview_questions(user_id, data):
    with repo.transaction() as connection:
        report, _ = build_preview(connection, user_id, data)
    if not report["errors"]:
        report["preview_token"] = create_preview_token(user_id, data)
    return report


def commit_questions(user_id, data, preview_token):
    verify_preview_token(preview_token, user_id, data)
    try:
        with repo.transaction() as connection:
            repo.lock_import_owner(connection, user_id)
            report, inserts = build_preview(connection, user_id, data)
            if report["errors"]:
                raise QuizImportError(422, "Question import validation failed. Preview this file again.")
            repo.insert_questions(connection, user_id, inserts, origin="csv")
            return {"inserted": len(inserts), "unchanged": report["unchanged"]}
    except IntegrityError:
        raise QuizImportError(409, "Question import conflicts with current data. Preview this file again.") from None
