"""Deterministic quiz validation, immutable attempt snapshots and locked grading."""
from decimal import Decimal, ROUND_HALF_UP

from app.ai.draft_receipts import DraftReceiptError, verify_draft_receipt

from app.repositories import quizzes as repo
from app.schemas.quizzes import ArchiveInput, QuestionInput

PUBLIC_QUESTION_FIELDS = ("id", "question_type", "prompt", "options", "subject_id", "topic_id", "resource_id", "source_page")
ATTEMPT_FIELDS = ("id", "quiz_id", "title", "status", "started_at", "completed_at", "score_value", "total_questions", "score_percent")


class QuizError(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def required(row, kind):
    if row is None:
        raise QuizError(404, f"{kind} not found.")
    return row


def validate_question_associations(connection, user_id, data):
    if not repo.valid_associations(connection, data.subject_id, data.topic_id):
        raise QuizError(422, "Choose an active subject and its matching topic.")
    if not repo.valid_resource(connection, user_id, data.resource_id, data.source_page):
        raise QuizError(422, "Choose an owned resource and an existing PDF source page.")


def validate_answer(question, keys):
    allowed = {o["key"] for o in question["options"]}
    if len(set(keys)) != len(keys) or not set(keys) <= allowed or (question["question_type"] != "multi_select" and len(keys) > 1):
        raise QuizError(422, "Selected keys must match this question's options and type.")


def grade_snapshot(snapshot, selections):
    results = []
    for question in snapshot:
        keys = selections.get(str(question["id"]), [])
        correct = bool(keys) and set(keys) == set(question["correct_keys"])
        results.append({"question_id": question["id"], "selected_keys": keys, "is_correct": correct})
    score = sum(result["is_correct"] for result in results)
    percent = float((Decimal(score) * 100 / Decimal(len(snapshot))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    return score, percent, results


def public_question(question):
    result = {key: question[key] for key in PUBLIC_QUESTION_FIELDS}
    result["options"] = [{"key": option["key"], "text": option["text"]} for option in question["options"]]
    return result


def project_attempt(row, answers):
    result = {key: row[key] for key in ATTEMPT_FIELDS}
    result["questions"] = []
    for question in row["snapshot"]:
        answer = answers.get(str(question["id"]), {})
        item = public_question(question)
        item["selected_keys"] = answer.get("selected_keys", [])
        if row["status"] == "completed":
            item.update(correct_keys=question["correct_keys"], explanation=question["explanation"], is_correct=answer.get("is_correct", False))
        result["questions"].append(item)
    return result


def _attempt(connection, user_id, row):
    return project_attempt(row, repo.answers(connection, user_id, row["id"]))


def list_questions(user_id, **filters):
    with repo.transaction() as connection:
        return repo.list_questions(connection, user_id, **filters)


def get_question(user_id, question_id):
    with repo.transaction() as connection:
        return required(repo.get_question(connection, user_id, question_id), "Question")


def create_question(user_id, data):
    provenance = _draft_provenance(user_id, data)
    with repo.transaction() as connection:
        repo.lock_import_owner(connection, user_id)
        validate_question_associations(connection, user_id, data)
        if repo.find_import_question(connection, user_id, repo.question_hashes(data)[0]):
            raise QuizError(409, "A question with this subject, topic and prompt already exists.")
        if provenance is not None:
            return repo.insert_question(connection, user_id, data, origin="ai", ai_provenance=provenance)
        return repo.insert_question(connection, user_id, data)


def _draft_provenance(user_id, data):
    if data.ai_draft_receipt is None:
        return None
    try:
        return verify_draft_receipt(data.ai_draft_receipt, user_id, "question").model_dump(mode="json")
    except DraftReceiptError as error:
        raise QuizError(error.status_code, error.detail) from None


def patch_question(user_id, question_id, data):
    with repo.transaction() as connection:
        repo.lock_import_owner(connection, user_id)
        required(repo.lock_question(connection, user_id, question_id), "Question")
        current = required(repo.get_question(connection, user_id, question_id), "Question")
        if isinstance(data, ArchiveInput):
            repo.archive(connection, "question", user_id, question_id)
        else:
            if current["is_archived"]:
                raise QuizError(409, "Archived questions cannot be edited.")
            validate_question_associations(connection, user_id, data)
            duplicate = repo.find_import_question(connection, user_id, repo.question_hashes(data)[0])
            if duplicate and duplicate["id"] != question_id:
                raise QuizError(409, "A question with this subject, topic and prompt already exists.")
            provenance = _draft_provenance(user_id, data)
            if provenance is not None:
                repo.update_question(connection, user_id, question_id, data, ai_provenance=provenance)
            else:
                repo.update_question(connection, user_id, question_id, data)
        return repo.get_question(connection, user_id, question_id)


def _quiz_detail(connection, user_id, quiz):
    ids = repo.quiz_question_ids(connection, user_id, quiz["id"])
    questions = repo.get_questions(connection, user_id, ids)
    return {**quiz, "questions": [public_question(required(questions.get(qid), "Question")) for qid in ids]}


def _validate_quiz(connection, user_id, data):
    if not repo.valid_associations(connection, data.subject_id, data.topic_id):
        raise QuizError(422, "Choose an active subject and its matching topic.")
    # The batch query locks rows in stable UUID order before loading options.
    questions = repo.get_questions(connection, user_id, data.question_ids, lock=True)
    for qid in data.question_ids:
        question = required(questions.get(qid), "Question")
        if question["is_archived"]:
            raise QuizError(422, "Choose active questions from your question bank.")


def list_quizzes(user_id, **filters):
    with repo.transaction() as connection:
        return repo.list_quizzes(connection, user_id, **filters)


def get_quiz(user_id, quiz_id):
    with repo.transaction() as connection:
        return _quiz_detail(connection, user_id, required(repo.get_quiz(connection, user_id, quiz_id), "Quiz"))


def create_quiz(user_id, data):
    with repo.transaction() as connection:
        _validate_quiz(connection, user_id, data)
        return _quiz_detail(connection, user_id, repo.write_quiz(connection, user_id, data))


def patch_quiz(user_id, quiz_id, data):
    with repo.transaction() as connection:
        current = required(repo.get_quiz(connection, user_id, quiz_id, lock=True), "Quiz")
        if isinstance(data, ArchiveInput):
            repo.archive(connection, "quiz", user_id, quiz_id)
            current = repo.get_quiz(connection, user_id, quiz_id)
        else:
            if current["is_archived"]:
                raise QuizError(409, "Archived quizzes cannot be edited.")
            _validate_quiz(connection, user_id, data)
            current = repo.write_quiz(connection, user_id, data, quiz_id)
        return _quiz_detail(connection, user_id, current)


def start_attempt(user_id, quiz_id):
    with repo.transaction() as connection:
        quiz = required(repo.get_quiz(connection, user_id, quiz_id, lock=True), "Quiz")
        existing = repo.active_attempt(connection, user_id, quiz_id)
        if existing:
            return _attempt(connection, user_id, required(repo.get_attempt(connection, user_id, existing, lock=True), "Attempt"))
        if quiz["is_archived"]:
            raise QuizError(409, "Archived quizzes cannot start new attempts.")
        ids = repo.quiz_question_ids(connection, user_id, quiz_id)
        # Hold question rows until the complete snapshot is persisted.
        questions = repo.get_questions(connection, user_id, ids, lock=True)
        for qid in ids:
            required(questions.get(qid), "Question")
        if not ids or any(q["is_archived"] for q in questions.values()):
            raise QuizError(409, "This quiz requires active questions before starting.")
        snapshot = []
        for qid in ids:
            q = questions[qid]
            frozen = QuestionInput.model_validate({key: q[key] for key in QuestionInput.model_fields if key in q}).model_dump(mode="json")
            snapshot.append({"id": str(qid), **frozen})
        return _attempt(connection, user_id, repo.insert_attempt(connection, user_id, quiz, snapshot))


def list_attempts(user_id, **filters):
    with repo.transaction() as connection:
        return repo.list_attempts(connection, user_id, **filters)


def get_attempt(user_id, attempt_id, *, results=False):
    with repo.transaction() as connection:
        # Readers use the same lock so they cannot mix pre-submit metadata and graded answers.
        row = required(repo.get_attempt(connection, user_id, attempt_id, lock=True), "Attempt")
        if results and row["status"] != "completed":
            raise QuizError(409, "Submit this attempt before viewing results.")
        return _attempt(connection, user_id, row)


def save_answer(user_id, attempt_id, data):
    with repo.transaction() as connection:
        row = required(repo.get_attempt(connection, user_id, attempt_id, lock=True), "Attempt")
        if row["status"] != "in_progress":
            raise QuizError(409, "Completed attempts cannot be changed.")
        question = next((q for q in row["snapshot"] if q["id"] == str(data.question_id)), None)
        if question is None:
            raise QuizError(422, "Question does not belong to this attempt.")
        validate_answer(question, data.selected_keys)
        repo.save_answer(connection, user_id, attempt_id, data.question_id, data.selected_keys)
        return _attempt(connection, user_id, row)


def complete_attempt(user_id, attempt_id):
    with repo.transaction() as connection:
        row = required(repo.get_attempt(connection, user_id, attempt_id, lock=True), "Attempt")
        if row["status"] == "completed":
            return _attempt(connection, user_id, row)
        answers = repo.answers(connection, user_id, attempt_id)
        score, percent, results = grade_snapshot(row["snapshot"], {qid: a["selected_keys"] for qid, a in answers.items()})
        for answer in results:
            repo.save_answer(connection, user_id, attempt_id, answer["question_id"], answer["selected_keys"], is_correct=answer["is_correct"])
        row = repo.finish_attempt(connection, user_id, attempt_id, score, percent)
        return _attempt(connection, user_id, row)
