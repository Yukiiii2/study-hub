"""Focused quiz validation, frozen grading and response privacy checks."""
import importlib.util
import unittest
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
from unittest.mock import patch
from uuid import uuid4

from pydantic import ValidationError


def question(**changes):
    data = dict(question_type="single_select", prompt="A question?", options=[{"key": "A", "text": "One"}, {"key": "B", "text": "Two"}], correct_keys=["A"])
    data.update(changes)
    return data


class QuizChecks(unittest.TestCase):
    def test_quiz_core_exists(self):
        self.assertIsNotNone(importlib.util.find_spec("app.schemas.quizzes"), "Quiz schemas are missing")

    def test_question_rejects_invalid_keys_cardinality_and_relationships(self):
        from app.schemas.quizzes import QuestionInput
        for changes in ({"correct_keys": ["C"]}, {"correct_keys": ["A", "B"]}, {"correct_keys": []},
                        {"prompt": "  "}, {"topic_id": uuid4()}, {"source_page": 1}, {"user_id": uuid4()},
                        {"options": [{"key": "A", "text": "One"}, {"key": "A", "text": "Two"}]},
                        {"question_type": "true_false"}):
            with self.subTest(changes=changes), self.assertRaises(ValidationError):
                QuestionInput.model_validate(question(**changes))

    def test_valid_types_and_exact_set_grading(self):
        from app.schemas.quizzes import QuestionInput
        from app.services.quizzes import grade_snapshot
        a = QuestionInput.model_validate(question(question_type="multi_select", correct_keys=["A", "B"])).model_dump(mode="json")
        b = QuestionInput.model_validate(question(question_type="true_false", options=[{"key": "TRUE", "text": "True"}, {"key": "FALSE", "text": "False"}], correct_keys=["TRUE"])).model_dump(mode="json")
        a["id"], b["id"] = str(uuid4()), str(uuid4())
        score, percent, results = grade_snapshot([a, b], {a["id"]: ["B", "A"]})
        self.assertEqual((score, percent), (1, 50.0))
        self.assertEqual([r["is_correct"] for r in results], [True, False])
        self.assertEqual(grade_snapshot([a], {a["id"]: ["A"]})[:2], (0, 0.0))

    def test_taking_projection_hides_secrets_until_completed(self):
        from app.services.quizzes import project_attempt
        item = question()
        item.update(id=str(uuid4()), explanation="Private explanation", subject_id=None, topic_id=None, resource_id=None, source_page=None, user_id="secret")
        row = dict(id=uuid4(), quiz_id=uuid4(), title="Quiz", status="in_progress", started_at=datetime.now(timezone.utc), completed_at=None, score_value=None, total_questions=1, score_percent=None, snapshot=[item], user_id="secret")
        result = project_attempt(row, {item["id"]: {"selected_keys": ["B"], "is_correct": False}})
        self.assertNotIn("snapshot", result)
        self.assertNotIn("user_id", result)
        self.assertNotIn("correct_keys", result["questions"][0])
        self.assertNotIn("explanation", result["questions"][0])
        self.assertNotIn("is_correct", result["questions"][0])
        self.assertEqual(result["questions"][0]["selected_keys"], ["B"])
        row.update(status="completed", completed_at=datetime.now(timezone.utc), score_value=0, score_percent=0)
        completed = project_attempt(row, {item["id"]: {"selected_keys": ["B"], "is_correct": False}})
        self.assertEqual(completed["questions"][0]["correct_keys"], ["A"])
        self.assertEqual(completed["questions"][0]["explanation"], "Private explanation")

    def test_answer_tampering_and_duplicate_selections_rejected(self):
        from app.services.quizzes import validate_answer, QuizError
        item = question()
        for keys in (["C"], ["A", "B"], ["A", "A"]):
            with self.subTest(keys=keys), self.assertRaises(QuizError) as caught:
                validate_answer(item, keys)
            self.assertEqual(caught.exception.status_code, 422)
        validate_answer(item, [])

    def test_percentage_counts_unanswered_and_rounds(self):
        from app.services.quizzes import grade_snapshot
        items = [{**question(), "id": str(uuid4())} for _ in range(3)]
        self.assertEqual(grade_snapshot(items, {items[0]["id"]: ["A"]})[:2], (1, 33.33))

    def test_duplicate_option_text_is_rejected(self):
        from app.schemas.quizzes import QuestionInput
        with self.assertRaises(ValidationError):
            QuestionInput.model_validate(question(options=[{"key": "A", "text": " One "}, {"key": "B", "text": "one"}]))

    def test_quiz_rejects_duplicated_questions_and_owner_fields(self):
        from app.schemas.quizzes import QuizInput
        qid = uuid4()
        for data in ({"title": "Quiz", "question_ids": [qid, qid]}, {"title": "Quiz", "question_ids": []},
                     {"title": "Quiz", "question_ids": [qid], "user_id": uuid4()},
                     {"title": "Quiz", "question_ids": [qid], "topic_id": uuid4()}):
            with self.subTest(data=data), self.assertRaises(ValidationError):
                QuizInput.model_validate(data)

    def test_control_characters_are_invalid_before_database_write(self):
        from app.schemas.quizzes import QuestionInput, QuizInput
        for changes in ({"prompt": "Question\x00"}, {"explanation": "Answer\x1b"},
                        {"options": [{"key": "A", "text": "One\x7f"}, {"key": "B", "text": "Two"}]}):
            with self.subTest(changes=changes), self.assertRaises(ValidationError):
                QuestionInput.model_validate(question(**changes))
        with self.assertRaises(ValidationError):
            QuizInput(title="Quiz\nTitle", question_ids=[uuid4()])
        valid = QuestionInput.model_validate(question(prompt="Question\nPart two\t?", explanation="Line one\r\nLine two"))
        self.assertIn("\n", valid.prompt)


class AttemptStore:
    """External database stand-in retains writes while running real quiz services."""
    def __init__(self):
        self.user = uuid4()
        self.qid = uuid4()
        self.attempt_id = uuid4()
        self.selected = {}
        item = {**question(), "id": str(self.qid), "explanation": "Frozen explanation", "subject_id": None, "topic_id": None, "resource_id": None, "source_page": None}
        self.row = dict(id=self.attempt_id, quiz_id=uuid4(), title="Frozen title", status="in_progress", snapshot=[item], started_at=datetime.now(timezone.utc), completed_at=None, score_value=None, total_questions=1, score_percent=None)

    @contextmanager
    def transaction(self):
        yield object()

    def get_attempt(self, connection, user_id, attempt_id, *, lock=False):
        if not lock:
            raise AssertionError("Service must lock attempts for consistent reads and mutations")
        return deepcopy(self.row) if user_id == self.user and attempt_id == self.attempt_id else None

    def answers(self, connection, user_id, attempt_id):
        return deepcopy(self.selected)

    def save_answer(self, connection, user_id, attempt_id, question_id, selected_keys, *, is_correct=None):
        self.selected[str(question_id)] = dict(selected_keys=list(selected_keys), is_correct=is_correct)

    def finish_attempt(self, connection, user_id, attempt_id, score, percent):
        self.row.update(status="completed", completed_at=datetime.now(timezone.utc), score_value=score, score_percent=percent)
        return deepcopy(self.row)


class AttemptLifecycleChecks(unittest.TestCase):
    def setUp(self):
        self.store = AttemptStore()

    def test_saved_answer_reload_and_idempotent_submission(self):
        from app.schemas.quizzes import AnswerInput
        from app.services import quizzes as service
        store = self.store
        with patch.object(service, "repo", store):
            saved = service.save_answer(store.user, store.attempt_id, AnswerInput(question_id=store.qid, selected_keys=["A"]))
            self.assertEqual(saved["questions"][0]["selected_keys"], ["A"])
            self.assertNotIn("is_correct", saved["questions"][0])
            reloaded = service.get_attempt(store.user, store.attempt_id)
            self.assertEqual(reloaded["questions"][0]["selected_keys"], ["A"])
            completed = service.complete_attempt(store.user, store.attempt_id)
            self.assertEqual(completed["score_value"], 1)
            self.assertEqual(completed["questions"][0]["correct_keys"], ["A"])
            repeated = service.complete_attempt(store.user, store.attempt_id)
            self.assertEqual(repeated, completed)
            with self.assertRaises(service.QuizError) as caught:
                service.save_answer(store.user, store.attempt_id, AnswerInput(question_id=store.qid, selected_keys=["B"]))
            self.assertEqual(caught.exception.status_code, 409)
            self.assertEqual(service.get_attempt(store.user, store.attempt_id), completed)

    def test_results_before_submission_and_cross_owner_denied(self):
        from app.services import quizzes as service
        store = self.store
        with patch.object(service, "repo", store):
            with self.assertRaises(service.QuizError) as premature:
                service.get_attempt(store.user, store.attempt_id, results=True)
            self.assertEqual(premature.exception.status_code, 409)
            with self.assertRaises(service.QuizError) as foreign:
                service.complete_attempt(uuid4(), store.attempt_id)
            self.assertEqual(foreign.exception.status_code, 404)
            self.assertEqual(store.selected, {})

    def test_nonmember_question_cannot_persist_answer(self):
        from app.schemas.quizzes import AnswerInput
        from app.services import quizzes as service
        store = self.store
        with patch.object(service, "repo", store), self.assertRaises(service.QuizError) as caught:
            service.save_answer(store.user, store.attempt_id, AnswerInput(question_id=uuid4(), selected_keys=["A"]))
        self.assertEqual(caught.exception.status_code, 422)
        self.assertEqual(store.selected, {})

    def test_unanswered_submission_persists_zero_correctness(self):
        from app.services import quizzes as service
        store = self.store
        with patch.object(service, "repo", store):
            result = service.complete_attempt(store.user, store.attempt_id)
        self.assertEqual((result["score_value"], result["score_percent"]), (0, 0.0))
        self.assertFalse(result["questions"][0]["is_correct"])
        self.assertEqual(result["questions"][0]["selected_keys"], [])


class AssociationChecks(unittest.TestCase):
    def test_resource_ownership_and_pdf_page_validation(self):
        from app.repositories.quizzes import valid_resource
        class Result:
            def __init__(self, row):
                self.row = row
            def mappings(self):
                return self
            def first(self):
                return self.row
        class Connection:
            def __init__(self, row):
                self.row = row
            def execute(self, query, params):
                self.query, self.params = str(query), params
                return Result(self.row)
        user, rid = uuid4(), uuid4()
        connection = Connection({"resource_type": "pdf", "page_count": 2})
        self.assertTrue(valid_resource(connection, user, rid, 2))
        self.assertFalse(valid_resource(connection, user, rid, 3))
        self.assertEqual(connection.params, {"user_id": user, "id": rid})
        self.assertIn("user_id=:user_id", connection.query)
        self.assertIn("FOR SHARE", connection.query)
        self.assertFalse(valid_resource(Connection(None), user, rid, None))
        self.assertFalse(valid_resource(Connection({"resource_type": "csv", "page_count": None}), user, rid, 1))

    def test_canonical_identity_and_current_content_distinguish_edit(self):
        from app.schemas.quizzes import QuestionInput
        from app.repositories.quizzes import question_hashes
        first = QuestionInput.model_validate(question(prompt="A  question?"))
        same = QuestionInput.model_validate(question(options=[{"key": "B", "text": "Two"}, {"key": "A", "text": "One"}]))
        edited = QuestionInput.model_validate(question(explanation="Added explanation"))
        self.assertEqual(question_hashes(first), question_hashes(same))
        self.assertEqual(question_hashes(first)[0], question_hashes(edited)[0])
        self.assertNotEqual(question_hashes(first)[1], question_hashes(edited)[1])


class QuizApiChecks(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        import httpx
        from app.main import app
        from app.core.auth import get_current_user
        from app.schemas.auth import AuthenticatedUser
        self.app, self.auth = app, get_current_user
        self.store = AttemptStore()
        app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id=self.store.user, email=None)
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")

    async def asyncTearDown(self):
        await self.client.aclose()
        self.app.dependency_overrides.pop(self.auth, None)

    async def test_http_taking_save_and_results_use_safe_projection(self):
        from app.services import quizzes as service
        store = self.store
        path = f"/api/quiz-attempts/{store.attempt_id}"
        with patch.object(service, "repo", store):
            saved = await self.client.post(path + "/answers", json={"question_id": str(store.qid), "selected_keys": ["A"]})
            self.assertEqual(saved.status_code, 200)
            self.assertNotIn("correct_keys", saved.json()["questions"][0])
            self.assertNotIn("explanation", saved.json()["questions"][0])
            self.assertNotIn("snapshot", saved.json())
            premature = await self.client.get(path + "/results")
            self.assertEqual(premature.status_code, 409)
            completed = await self.client.post(path + "/complete")
            self.assertEqual(completed.status_code, 200)
            self.assertEqual(completed.json()["questions"][0]["correct_keys"], ["A"])
            self.assertEqual(completed.json()["questions"][0]["explanation"], "Frozen explanation")

    async def test_http_forbids_client_grading_and_sanitizes_database_errors(self):
        from sqlalchemy.exc import SQLAlchemyError
        from app.services import quizzes as service
        store = self.store
        path = f"/api/quiz-attempts/{store.attempt_id}/answers"
        invalid = await self.client.post(path, json={"question_id": str(store.qid), "selected_keys": [], "is_correct": True})
        self.assertEqual(invalid.status_code, 422)
        with patch.object(service, "list_questions", side_effect=SQLAlchemyError("private provider payload")):
            unavailable = await self.client.get("/api/questions")
        self.assertEqual(unavailable.status_code, 503)
        self.assertNotIn("private provider payload", unavailable.text)

    async def test_question_routes_require_authentication(self):
        self.app.dependency_overrides.pop(self.auth, None)
        response = await self.client.get("/api/questions")
        self.assertEqual(response.status_code, 401)


class BatchQueryResult:
    def __init__(self, rows):
        self.rows = rows

    def mappings(self):
        return self

    def all(self):
        return self.rows

    def first(self):
        return self.rows[0] if self.rows else None

    def scalar_one(self):
        return len(self.rows)

    def scalars(self):
        return iter(self.rows)


class BatchQueryConnection:
    """Capture real repository queries; database-shaped fixtures need no live DB."""
    def __init__(self, count=100):
        from uuid import UUID
        self.ids = [UUID(int=index + 1) for index in range(count)]
        self.rows = [{**question(), "id": qid, "explanation": "Private key explanation", "subject_id": None,
                      "topic_id": None, "resource_id": None, "source_page": None, "origin": "manual",
                      "is_archived": False, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)}
                     for qid in reversed(self.ids)]
        self.calls = []

    def execute(self, query, params):
        sql = str(query)
        self.calls.append((sql, params))
        if "FROM public.quiz_questions" in sql:
            return BatchQueryResult(list(reversed(self.ids)))
        if "FROM public.question_options" in sql:
            ids = params.get("question_ids", [params.get("id")])
            rows = [{"question_id": qid, "option_key": key, "text": label, "is_correct": key == "A"}
                    for qid in sorted(ids) for key, label in (("A", "One"), ("B", "Two"))]
            return BatchQueryResult(rows)
        if "FROM public.questions" in sql:
            rows = [{key: value for key, value in row.items() if key not in {"options", "correct_keys"}} for row in self.rows]
            if "question_ids" in params:
                rows = [row for row in rows if row["id"] in params["question_ids"]]
            elif "id" in params:
                rows = [row for row in rows if row["id"] == params["id"]]
            if "ORDER BY id" in sql:
                rows.sort(key=lambda row: row["id"])
            return BatchQueryResult(rows)
        raise AssertionError("Unexpected database query")


class BatchedQuestionChecks(unittest.TestCase):
    def test_hundred_question_list_loads_options_in_one_owner_bound_query(self):
        from app.repositories import quizzes as repo
        user = uuid4()
        connection = BatchQueryConnection()
        result = repo.list_questions(connection, user, limit=100)
        self.assertEqual(len(connection.calls), 3, "List should use count, questions and one option query")
        self.assertEqual([row["id"] for row in result["questions"]], list(reversed(connection.ids)))
        self.assertEqual(result["total"], 100)
        for row in result["questions"]:
            self.assertEqual(row["options"], [{"key": "A", "text": "One"}, {"key": "B", "text": "Two"}])
            self.assertEqual(row["correct_keys"], ["A"])
        sql, params = connection.calls[-1]
        self.assertIn("user_id=:user_id", sql)
        self.assertIn("ORDER BY question_id,display_order", sql)
        self.assertEqual(params["user_id"], user)
        self.assertEqual(set(params["question_ids"]), set(connection.ids))

    def test_quiz_detail_preserves_membership_order_and_public_projection(self):
        from app.services import quizzes as service
        user = uuid4()
        connection = BatchQueryConnection()
        detail = service._quiz_detail(connection, user, {"id": uuid4()})
        self.assertEqual(len(connection.calls), 3, "Quiz detail should load IDs, questions and options once each")
        self.assertEqual([q["id"] for q in detail["questions"]], list(reversed(connection.ids)))
        self.assertNotIn("correct_keys", detail["questions"][0])
        self.assertNotIn("explanation", detail["questions"][0])
        self.assertNotIn("is_correct", detail["questions"][0]["options"][0])

    def test_builder_validation_locks_owned_questions_once_in_stable_order(self):
        from app.schemas.quizzes import QuizInput
        from app.services import quizzes as service
        user = uuid4()
        connection = BatchQueryConnection()
        data = QuizInput(title="Quiz", question_ids=list(reversed(connection.ids)))
        service._validate_quiz(connection, user, data)
        self.assertEqual(len(connection.calls), 2)
        sql, params = connection.calls[0]
        self.assertIn("user_id=:user_id", sql)
        self.assertIn("ORDER BY id FOR SHARE", sql)
        self.assertEqual(params["user_id"], user)
        self.assertEqual(params["question_ids"], connection.ids)

    def test_batch_builder_rejects_missing_or_archived_questions(self):
        from app.schemas.quizzes import QuizInput
        from app.services import quizzes as service
        connection = BatchQueryConnection(1)
        with self.assertRaises(service.QuizError) as missing:
            service._validate_quiz(connection, uuid4(), QuizInput(title="Quiz", question_ids=[uuid4()]))
        self.assertEqual(missing.exception.status_code, 404)
        connection.rows[0]["is_archived"] = True
        with self.assertRaises(service.QuizError) as archived:
            service._validate_quiz(connection, uuid4(), QuizInput(title="Quiz", question_ids=connection.ids))
        self.assertEqual(archived.exception.status_code, 422)

    def test_import_existing_payloads_are_loaded_in_two_owned_queries(self):
        from app.schemas.quizzes import QuestionInput
        from app.repositories import quizzes as repo
        self.assertTrue(hasattr(repo, "find_import_questions"), "Batch import lookup is missing")
        connection = BatchQueryConnection(2)
        for index, row in enumerate(connection.rows):
            row["prompt"] = f"Question {index}?"
            data = QuestionInput.model_validate({key: row[key] for key in QuestionInput.model_fields})
            row["identity_hash"], row["content_hash"] = repo.question_hashes(data)
        hashes = [row["identity_hash"] for row in connection.rows]
        user = uuid4()
        result = repo.find_import_questions(connection, user, hashes)
        self.assertEqual(set(result), set(hashes))
        self.assertEqual(len(connection.calls), 2)
        self.assertEqual(connection.calls[0][1]["user_id"], user)
        self.assertEqual(set(connection.calls[0][1]["identity_hashes"]), set(hashes))
        self.assertIn("user_id=:user_id", connection.calls[0][0])
        for row in result.values():
            self.assertEqual(row["correct_keys"], ["A"])

    def test_five_hundred_questions_insert_in_two_executemany_calls(self):
        from app.schemas.quizzes import QuestionInput
        from app.repositories import quizzes as repo
        self.assertTrue(hasattr(repo, "insert_questions"), "Bulk import insertion is missing")
        class Connection:
            def __init__(self):
                self.calls = []
            def execute(self, query, params):
                self.calls.append((str(query), params))
        connection = Connection()
        user = uuid4()
        entries = []
        for index in range(500):
            data = QuestionInput.model_validate(question(prompt=f"Question {index}?"))
            entries.append((data, *repo.question_hashes(data)))
        repo.insert_questions(connection, user, entries, origin="csv")
        self.assertEqual(len(connection.calls), 2)
        question_values, option_values = [params for query, params in connection.calls]
        self.assertEqual(len(question_values), 500)
        self.assertEqual(len(option_values), 1000)
        ids = {row["id"] for row in question_values}
        self.assertEqual(len(ids), 500)
        self.assertEqual({row["user_id"] for row in question_values + option_values}, {user})
        self.assertEqual({row["origin"] for row in question_values}, {"csv"})
        self.assertEqual({row["question_id"] for row in option_values}, ids)
        self.assertEqual([row["is_correct"] for row in option_values[:2]], [True, False])
