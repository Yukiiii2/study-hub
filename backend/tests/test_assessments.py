"""Focused assessment validation, lifecycle and readiness checks."""
import importlib.util
import json
import unittest
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import patch
from uuid import uuid4

from pydantic import ValidationError

NOW = datetime(2026, 10, 9, 12, tzinfo=timezone.utc)


class AssessmentChecks(unittest.TestCase):
    def test_assessment_domain_exists(self):
        self.assertIsNotNone(importlib.util.find_spec("app.services.assessments"))

    def test_definition_rejects_untrusted_fields_duplicates_and_nulls(self):
        from app.schemas.assessments import AssessmentCreate, AssessmentPatch
        topic = uuid4()
        for extra in ({"user_id": uuid4()}, {"source_key": "import"}, {"topic_ids": [topic, topic]},
                      {"topic_ids": [uuid4() for _ in range(501)]}, {"title": " "}, {"scheduled_at": "2026-10-09T10:00:00"}):
            with self.subTest(extra=str(extra)[:60]), self.assertRaises(ValidationError):
                AssessmentCreate.model_validate({"title": "Exam", **extra})
        for extra in ({"title": None}, {"status": None}, {"topic_ids": None}, {"subject_ids": None}):
            with self.assertRaises(ValidationError):
                AssessmentPatch.model_validate(extra)

    def test_score_pair_completion_and_finite_numbers_are_required(self):
        from app.schemas.assessments import AttemptCreate
        for values in ({"score": 1}, {"max_score": 3}, {"score": -1, "max_score": 3},
                       {"score": 4, "max_score": 3}, {"score": 0, "max_score": 0},
                       {"score": "NaN", "max_score": 3}, {"score": "Infinity", "max_score": 3},
                       {"score": True, "max_score": 3}, {"percentage": 80},
                       {"score": "0.00001", "max_score": 3}, {"score": "1e1000", "max_score": "1e1000"},
                       {"score": 1, "max_score": 3, "completed_at": None},
                       {"started_at": NOW, "completed_at": "2026-10-08T12:00:00Z"}):
            with self.subTest(values=values), self.assertRaises(ValidationError):
                AttemptCreate.model_validate({"completed_at": NOW, **values})

    def test_percentage_rounding_and_numeric_json(self):
        from app.services.assessments import percentage
        from app.schemas.assessments import AttemptResponse
        self.assertEqual(percentage(Decimal(1), Decimal(3)), Decimal("33.3333"))
        self.assertIsNone(percentage(0, 0))
        row = AttemptResponse(id=uuid4(), assessment_id=uuid4(), started_at=None,
                              completed_at=NOW, score=Decimal(1), max_score=Decimal(3),
                              percentage=percentage(1, 3), notes=None, created_at=NOW, updated_at=NOW)
        values = json.loads(row.model_dump_json())
        self.assertEqual(values["percentage"], 33.3333)
        self.assertEqual(values["score"], 1)


class Store:
    def __init__(self):
        self.user = uuid4()
        self.subject = uuid4()
        self.topic = uuid4()
        self.rows = {}
        self.attempts = {}
        self.readonly = []

    @contextmanager
    def transaction(self, *, readonly=False):
        saved = deepcopy((self.rows, self.attempts))
        self.readonly.append(readonly)
        try:
            yield object()
        except Exception:
            self.rows, self.attempts = saved
            raise

    def valid_coverage(self, connection, topic_ids, subject_ids):
        return set(topic_ids) <= {self.topic} and set(subject_ids) <= {self.subject} and not (topic_ids and subject_ids)

    def get_assessment(self, connection, user_id, assessment_id, *, lock=False):
        return deepcopy(self.rows.get(assessment_id)) if user_id == self.user else None

    def write_assessment(self, connection, user_id, data, assessment_id=None):
        assessment_id = assessment_id or uuid4()
        row = {**data.model_dump(), "id": assessment_id, "created_at": NOW, "updated_at": NOW,
               "coverage_topics": [], "coverage_subjects": [], "topic_count": len(data.topic_ids)}
        self.rows[assessment_id] = row
        return deepcopy(row)

    def archive_assessment(self, connection, user_id, assessment_id):
        self.rows[assessment_id]["status"] = "archived"

    def get_attempt(self, connection, user_id, attempt_id, *, lock=False):
        return deepcopy(self.attempts.get(attempt_id)) if user_id == self.user else None

    def write_attempt(self, connection, user_id, assessment_id, values, attempt_id=None):
        attempt_id = attempt_id or uuid4()
        row = {**values, "id": attempt_id, "assessment_id": assessment_id, "created_at": NOW, "updated_at": NOW}
        self.attempts[attempt_id] = row
        return deepcopy(row)

    def list_attempts(self, connection, user_id, assessment_id, **filters):
        rows = [deepcopy(row) for row in self.attempts.values() if row["assessment_id"] == assessment_id]
        return {"attempts": rows, "total": len(rows)}

    def profile_timezone(self, connection, user_id):
        return "Asia/Taipei"

    def readiness_counts(self, connection, user_id, assessment_id, now, day_start):
        self.day_start = day_start
        return {"topic_count": 1, "total_videos": 3, "completed_videos": 1,
                "quiz_graded_answers": 4, "quiz_correct_answers": 1,
                "active_flashcards": 3, "reviewed_flashcards": 1, "due_flashcards": 2, "overdue_flashcards": 1}


class LifecycleChecks(unittest.TestCase):
    def setUp(self):
        from app.services import assessments as service
        from app.schemas.assessments import AssessmentCreate
        self.service = service
        self.store = Store()
        repo_patch = patch.object(service, "repo", self.store)
        clock_patch = patch.object(service, "_now", return_value=NOW)
        repo_patch.start()
        clock_patch.start()
        self.addCleanup(repo_patch.stop)
        self.addCleanup(clock_patch.stop)
        self.row = service.create_assessment(self.store.user, AssessmentCreate(title="Exam", topic_ids=[self.store.topic]))

    def test_partial_coverage_patch_validates_merged_state_and_rolls_back(self):
        from app.schemas.assessments import AssessmentPatch
        with self.assertRaises(self.service.AssessmentError) as caught:
            self.service.patch_assessment(self.store.user, self.row["id"], AssessmentPatch(subject_ids=[self.store.subject]))
        self.assertEqual(caught.exception.status_code, 422)
        self.assertEqual(self.store.rows[self.row["id"]]["subject_ids"], [])
        result = self.service.patch_assessment(self.store.user, self.row["id"], AssessmentPatch(topic_ids=[], subject_ids=[self.store.subject]))
        self.assertEqual(result["subject_ids"], [self.store.subject])

    def test_manual_correction_merged_validation_and_archive_preserve_history(self):
        from app.schemas.assessments import AttemptCreate, AttemptPatch
        result = self.service.create_attempt(self.store.user, self.row["id"], AttemptCreate(score=1, max_score=3, completed_at=NOW))
        with self.assertRaises(self.service.AssessmentError) as invalid:
            self.service.patch_attempt(self.store.user, result["id"], AttemptPatch(max_score=0))
        self.assertEqual(invalid.exception.status_code, 422)
        corrected = self.service.patch_attempt(self.store.user, result["id"], AttemptPatch(score=2))
        self.assertEqual(corrected["percentage"], Decimal("66.6667"))
        self.service.delete_assessment(self.store.user, self.row["id"])
        history = self.service.list_attempts(self.store.user, self.row["id"])
        self.assertEqual(history["total"], 1)
        self.assertEqual(history["attempts"][0]["score"], 2)
        for call in (lambda: self.service.create_attempt(self.store.user, self.row["id"], AttemptCreate()),
                     lambda: self.service.patch_attempt(self.store.user, result["id"], AttemptPatch(notes="edit"))):
            with self.assertRaises(self.service.AssessmentError) as archived:
                call()
            self.assertEqual(archived.exception.status_code, 409)

    def test_foreign_definition_and_attempt_return_404(self):
        from app.schemas.assessments import AttemptCreate, AttemptPatch
        result = self.service.create_attempt(self.store.user, self.row["id"], AttemptCreate())
        for call in (lambda: self.service.get_assessment(uuid4(), self.row["id"]),
                     lambda: self.service.patch_attempt(uuid4(), result["id"], AttemptPatch(notes="edit"))):
            with self.assertRaises(self.service.AssessmentError) as foreign:
                call()
            self.assertEqual(foreign.exception.status_code, 404)

    def test_detail_uses_readonly_snapshot_real_denominators_and_local_day(self):
        result = self.service.get_assessment(self.store.user, self.row["id"])
        ready = result["readiness"]
        self.assertTrue(self.store.readonly[-1])
        self.assertEqual(ready["video_completion_percentage"], Decimal("33.3333"))
        self.assertEqual(ready["quiz_accuracy_percentage"], Decimal("25.0000"))
        self.assertEqual(ready["quiz_graded_answers"], 4)
        self.assertEqual(self.store.day_start, datetime(2026, 10, 8, 16, tzinfo=timezone.utc))
        self.assertEqual(ready["timezone"], "Asia/Taipei")

    def test_empty_coverage_readiness_has_null_percentages(self):
        counts = {key: 0 for key in ("topic_count", "total_videos", "completed_videos", "quiz_graded_answers",
                                     "quiz_correct_answers", "active_flashcards", "reviewed_flashcards", "due_flashcards", "overdue_flashcards")}
        with patch.object(self.store, "readiness_counts", return_value=counts):
            ready = self.service.get_assessment(self.store.user, self.row["id"])["readiness"]
        self.assertIsNone(ready["video_completion_percentage"])
        self.assertIsNone(ready["quiz_accuracy_percentage"])

    def test_attempt_score_pair_can_be_cleared_together_but_not_separately(self):
        from app.schemas.assessments import AttemptCreate, AttemptPatch
        result = self.service.create_attempt(self.store.user, self.row["id"], AttemptCreate(score=0, max_score=10, completed_at=NOW))
        with self.assertRaises(self.service.AssessmentError) as incomplete:
            self.service.patch_attempt(self.store.user, result["id"], AttemptPatch(score=None))
        self.assertEqual(incomplete.exception.status_code, 422)
        cleared = self.service.patch_attempt(self.store.user, result["id"], AttemptPatch(score=None, max_score=None))
        self.assertIsNone(cleared["percentage"])
        self.assertIsNone(cleared["score"])
        self.assertEqual(cleared["completed_at"], NOW)


class RouteChecks(unittest.TestCase):
    def setUp(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from app.api.assessments import router
        from app.core.auth import get_current_user
        from app.schemas.auth import AuthenticatedUser
        from app.services import assessments as service
        self.service = service
        self.store = Store()
        repo_patch = patch.object(service, "repo", self.store)
        repo_patch.start()
        self.addCleanup(repo_patch.stop)
        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id=self.store.user, email="test@example.com")
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def test_crud_status_codes_numeric_result_and_archived_conflict(self):
        created = self.client.post("/api/assessments", json={"title": "Exam"})
        self.assertEqual(created.status_code, 201)
        identity = created.json()["id"]
        attempt = self.client.post(f"/api/assessments/{identity}/attempts", json={"score": 1, "max_score": 3, "completed_at": NOW.isoformat()})
        self.assertEqual(attempt.status_code, 201)
        self.assertEqual(attempt.json()["percentage"], 33.3333)
        self.assertIsInstance(attempt.json()["score"], (int, float))
        archived = self.client.delete(f"/api/assessments/{identity}")
        self.assertEqual((archived.status_code, archived.content), (204, b""))
        self.assertEqual(self.client.get(f"/api/assessments/{identity}/attempts").json()["total"], 1)
        self.assertEqual(self.client.post(f"/api/assessments/{identity}/attempts", json={}).status_code, 409)

    def test_invalid_queries_fields_missing_rows_and_sanitized_outage(self):
        from sqlalchemy.exc import OperationalError
        for query in ("limit=101", "limit=0", "offset=-1", "status=unknown"):
            self.assertEqual(self.client.get("/api/assessments?" + query).status_code, 422)
        self.assertEqual(self.client.post("/api/assessments", json={"title": "Exam", "user_id": str(uuid4())}).status_code, 422)
        self.assertEqual(self.client.get(f"/api/assessments/{uuid4()}").status_code, 404)
        with patch.object(self.service, "get_assessment", side_effect=OperationalError("private SQL", {}, Exception("secret"))):
            response = self.client.get(f"/api/assessments/{uuid4()}")
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("private", response.text)
        self.assertNotIn("secret", response.text)


if __name__ == "__main__":
    unittest.main()
