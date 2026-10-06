"""Focused planner contract and recurrence checks; no live database writes."""
import unittest
from datetime import date, datetime, timezone
from uuid import UUID
from unittest.mock import patch

import httpx
from pydantic import ValidationError

from app.main import app
from app.core.auth import get_current_user
from app.schemas.auth import AuthenticatedUser

ID = UUID("00000000-0000-4000-8000-000000000001")


def event(**changes):
    return {"id": ID, "subject_id": None, "topic_id": None, "title": "Reading",
            "event_type": "reading", "start_at": datetime.fromisoformat("2026-10-05T09:00:00+08:00"),
            "end_at": datetime.fromisoformat("2026-10-05T10:00:00+08:00"), "timezone": "Asia/Manila",
            "status": "scheduled", "recurrence_rule": "FREQ=WEEKLY;BYDAY=MO,WE;UNTIL=20261014",
            "notes": None, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc), **changes}


class PlannerLogicChecks(unittest.TestCase):
    def test_unrepresentable_recurrence_boundaries_return_validation_error(self):
        from app.services.planner_recurrence import expand_events, occurrence, PlannerError
        first = event(start_at=datetime(1, 1, 1, 9, tzinfo=timezone.utc),
                      end_at=datetime(1, 1, 1, 10, tzinfo=timezone.utc), timezone="UTC",
                      recurrence_rule="FREQ=WEEKLY;BYDAY=MO")
        with self.assertRaises(PlannerError) as error:
            expand_events([first], [], datetime(1, 1, 1, tzinfo=timezone.utc), datetime(1, 1, 2, tzinfo=timezone.utc))
        self.assertEqual(error.exception.status_code, 422)
        last = event(start_at=datetime(9999, 12, 20, 9, tzinfo=timezone.utc),
                     end_at=datetime(9999, 12, 31, 10, tzinfo=timezone.utc), timezone="UTC",
                     recurrence_rule="FREQ=WEEKLY;BYDAY=MO")
        with self.assertRaises(PlannerError) as error:
            occurrence(last, date(9999, 12, 27))
        self.assertEqual(error.exception.status_code, 422)

    def test_generated_occurrence_requires_positive_actual_interval(self):
        from app.services.planner_recurrence import occurrence, PlannerError
        with patch("app.services.planner_recurrence.localize", side_effect=[
            datetime(2026, 10, 12, 10, tzinfo=timezone.utc), datetime(2026, 10, 12, 9, tzinfo=timezone.utc)
        ]):
            with self.assertRaises(PlannerError):
                occurrence(event(), date(2026, 10, 12))

    def test_outside_window_dst_gap_is_ignored_but_in_window_gap_is_reported(self):
        from app.services.planner_recurrence import expand_events, PlannerError
        series = event(timezone="America/New_York", recurrence_rule="FREQ=WEEKLY;BYDAY=SU",
                       start_at=datetime.fromisoformat("2026-03-01T02:30:00-05:00"),
                       end_at=datetime.fromisoformat("2026-03-01T03:30:00-05:00"))
        for start, end in (("2026-03-07T00:00:00-05:00", "2026-03-08T00:00:00-05:00"),
                           ("2026-03-09T00:00:00-04:00", "2026-03-10T00:00:00-04:00")):
            self.assertEqual(expand_events([series], [], datetime.fromisoformat(start), datetime.fromisoformat(end)), [])
        with self.assertRaises(PlannerError):
            expand_events([series], [], datetime.fromisoformat("2026-03-08T00:00:00-05:00"), datetime.fromisoformat("2026-03-09T00:00:00-04:00"))

    def test_title_and_notes_limits_match_planner_inputs(self):
        from app.schemas.planner import EventCreate, EventPatch, TaskCreate, TaskPatch, SessionCreate, SessionPatch
        for model, fields in ((EventCreate, {"start_at": "2026-10-05T09:00:00Z", "end_at": "2026-10-05T10:00:00Z"}),
                              (EventPatch, {}), (TaskCreate, {}), (TaskPatch, {})):
            with self.assertRaises(ValidationError):
                model(title="x" * 201, **fields)
        for model, fields in ((EventCreate, {"title": "Reading", "start_at": "2026-10-05T09:00:00Z", "end_at": "2026-10-05T10:00:00Z"}),
                              (EventPatch, {}), (SessionCreate, {}), (SessionPatch, {})):
            with self.assertRaises(ValidationError):
                model(notes="x" * 10001, **fields)

    def test_rule_anchor_end_and_series_status_are_validated(self):
        from app.services.planner_recurrence import validate_event, PlannerError
        for changes in ({"recurrence_rule": "FREQ=DAILY"}, {"recurrence_rule": "FREQ=WEEKLY;BYDAY=WE"},
                        {"recurrence_rule": "FREQ=WEEKLY;BYDAY=MO;UNTIL=20260230"},
                        {"recurrence_rule": "FREQ=WEEKLY;BYDAY=MO;UNTIL=20261001"}, {"status": "completed"},
                        {"topic_id": ID}, {"timezone": "Unknown/Nowhere"}):
            with self.assertRaises(PlannerError):
                validate_event(event(**changes))

    def test_suppressed_occurrence_and_half_open_overlap_boundaries(self):
        from app.services.planner_recurrence import expand_events
        snapshot = {**event(), "id": UUID(int=2), "study_event_id": ID, "occurrence_date": date(2026, 10, 5), "is_deleted": True}
        start = datetime.fromisoformat("2026-10-05T09:00:00+08:00")
        end = datetime.fromisoformat("2026-10-05T10:00:00+08:00")
        self.assertEqual(expand_events([event()], [snapshot], start, end), [])
        self.assertEqual(expand_events([event(recurrence_rule=None, end_at=start, start_at=datetime.fromisoformat("2026-10-05T08:00:00+08:00"))], [], start, end), [])
        self.assertEqual(expand_events([event(recurrence_rule=None, start_at=end, end_at=datetime.fromisoformat("2026-10-05T11:00:00+08:00"))], [], start, end), [])

    def test_session_inherits_occurrence_context_and_materializes_snapshot(self):
        from app.services import planner as service
        from app.schemas.planner import SessionCreate
        from contextlib import nullcontext
        stored = event(subject_id=ID, topic_id=UUID(int=3))
        saved = {"id": UUID(int=2)}
        with patch.object(service.repo, "transaction", return_value=nullcontext(object())), \
             patch.object(service.repo, "active_session", return_value=None), \
             patch.object(service.repo, "get_record", return_value=stored), \
             patch.object(service.repo, "get_snapshot", return_value=None), \
             patch.object(service.repo, "valid_associations", return_value=True), \
             patch.object(service.repo, "insert_record", side_effect=lambda c, k, u, d: saved if k == "occurrences" else d):
            result = service.create_session(ID, SessionCreate(study_event_id=ID, occurrence_date="2026-10-07"))
            self.assertEqual(result["subject_id"], ID)
            self.assertEqual(result["topic_id"], UUID(int=3))
            self.assertEqual(result["occurrence_id"], UUID(int=2))

    def test_patch_validates_merged_end_and_retains_omitted_fields(self):
        from app.services import planner as service
        from app.services.planner_recurrence import PlannerError
        from app.schemas.planner import EventPatch
        from contextlib import nullcontext
        stored = event(recurrence_rule=None)
        with patch.object(service.repo, "transaction", return_value=nullcontext(object())), \
             patch.object(service.repo, "get_record", return_value=stored), \
             patch.object(service.repo, "valid_associations", return_value=True), \
             patch.object(service.repo, "update_record", side_effect=lambda c, k, u, i, d: {**stored, **d}):
            with self.assertRaises(PlannerError):
                service.patch_event(ID, ID, EventPatch(start_at="2026-10-05T11:00:00+08:00"))
            result = service.patch_event(ID, ID, EventPatch(title="New"))
            self.assertEqual(result["title"], "New")
            self.assertEqual(result["end_at"].isoformat(), "2026-10-05T10:00:00+08:00")

    def test_task_schedule_rejects_changed_subject_and_nonpending_task(self):
        from app.services import planner as service
        from app.services.planner_recurrence import PlannerError
        from app.schemas.planner import EventCreate
        from contextlib import nullcontext
        body = EventCreate(title="New", subject_id=ID, start_at="2026-10-05T09:00:00+08:00", end_at="2026-10-05T10:00:00+08:00")
        task = {"subject_id": None, "topic_id": None, "status": "pending"}
        with patch.object(service.repo, "transaction", return_value=nullcontext(object())), patch.object(service.repo, "get_record", return_value=task):
            with self.assertRaises(PlannerError) as error:
                service.schedule_task(ID, ID, body)
            self.assertEqual(error.exception.status_code, 422)
            task["status"] = "completed"
            with self.assertRaises(PlannerError) as error:
                service.schedule_task(ID, ID, body)
            self.assertEqual(error.exception.status_code, 409)

    def test_request_fields_and_required_values_are_strict(self):
        from app.schemas.planner import EventCreate, EventPatch, TaskCreate, SessionPatch
        valid = {"title": "Reading", "start_at": "2026-10-05T09:00:00+08:00", "end_at": "2026-10-05T10:00:00+08:00"}
        for changes in ({"user_id": str(ID)}, {"title": " "}, {"start_at": "2026-10-05T09:00:00"}):
            with self.assertRaises(ValidationError):
                EventCreate(**{**valid, **changes})
        with self.assertRaises(ValidationError):
            EventPatch(title=None)
        with self.assertRaises(ValidationError):
            TaskCreate(title="Reading", status="scheduled")
        with self.assertRaises(ValidationError):
            SessionPatch(duration_seconds=100)

    def test_weekly_selected_days_and_inclusive_until(self):
        from app.services.planner_recurrence import expand_events
        rows = expand_events([event()], [], datetime.fromisoformat("2026-10-01T00:00:00+08:00"), datetime.fromisoformat("2026-10-16T00:00:00+08:00"))
        self.assertEqual([r["occurrence_date"] for r in rows], [date(2026, 10, 5), date(2026, 10, 7), date(2026, 10, 12), date(2026, 10, 14)])

    def test_moved_snapshot_replaces_original_and_survives_rule_edit(self):
        from app.services.planner_recurrence import expand_events
        snapshot = {**event(), "id": UUID(int=2), "study_event_id": ID, "occurrence_date": date(2026, 10, 7), "is_deleted": False,
                    "start_at": datetime.fromisoformat("2026-10-20T09:00:00+08:00"), "end_at": datetime.fromisoformat("2026-10-20T10:00:00+08:00")}
        start = datetime.fromisoformat("2026-10-20T00:00:00+08:00")
        rows = expand_events([event(recurrence_rule="FREQ=WEEKLY;BYDAY=MO")], [snapshot], start, datetime.fromisoformat("2026-10-21T00:00:00+08:00"))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["occurrence_id"], UUID(int=2))
        rows = expand_events([event()], [snapshot], datetime.fromisoformat("2026-10-07T00:00:00+08:00"), datetime.fromisoformat("2026-10-08T00:00:00+08:00"))
        self.assertEqual(rows, [])

    def test_dst_gap_and_fold_rejected_and_wall_clock_preserved(self):
        from app.services.planner_recurrence import localize, expand_events, PlannerError
        for value in (datetime(2026, 3, 8, 2, 30), datetime(2026, 11, 1, 1, 30)):
            with self.assertRaises(PlannerError):
                localize(value, "America/New_York")
        series = event(timezone="America/New_York", recurrence_rule="FREQ=WEEKLY;BYDAY=MO",
                       start_at=datetime.fromisoformat("2026-03-02T09:00:00-05:00"), end_at=datetime.fromisoformat("2026-03-02T10:00:00-05:00"))
        rows = expand_events([series], [], datetime.fromisoformat("2026-03-08T00:00:00Z"), datetime.fromisoformat("2026-03-10T00:00:00Z"))
        self.assertEqual(rows[0]["start_at"].isoformat(), "2026-03-09T09:00:00-04:00")

    def test_range_and_overflow_are_rejected(self):
        from app.services.planner_recurrence import expand_events, PlannerError
        start = datetime.fromisoformat("2026-10-05T00:00:00Z")
        end = datetime.fromisoformat("2026-10-06T00:00:00Z")
        with self.assertRaises(PlannerError):
            expand_events([event(id=UUID(int=i + 1), recurrence_rule=None) for i in range(2001)], [], start, end)
        with self.assertRaises(PlannerError):
            expand_events([], [], start, datetime.fromisoformat("2027-02-01T00:00:00Z"))


class PlannerApiChecks(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")

    async def asyncTearDown(self):
        app.dependency_overrides.clear()
        await self.client.aclose()

    async def test_every_domain_requires_authentication(self):
        for path in ("/api/study-plan/context", "/api/study-events", "/api/study-tasks", "/api/study-sessions"):
            self.assertEqual((await self.client.get(path)).status_code, 401)
        for path in ("/api/study-events", "/api/study-tasks", "/api/study-sessions"):
            self.assertEqual((await self.client.post(path, json={})).status_code, 401)

    async def test_ownership_missing_and_infrastructure_errors_are_sanitized(self):
        app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id=ID, email=None)
        with patch("app.api.planner.service.get_event", side_effect=lambda user_id, event_id: None):
            self.assertEqual((await self.client.get(f"/api/study-events/{ID}")).status_code, 404)
        from sqlalchemy.exc import SQLAlchemyError
        with patch("app.api.planner.service.get_context", side_effect=SQLAlchemyError("private detail")):
            response = await self.client.get("/api/study-plan/context")
            self.assertEqual(response.status_code, 503)
            self.assertNotIn("private detail", response.text)

    async def test_extra_fields_naive_ranges_and_invalid_null_patch_fail(self):
        app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id=ID, email=None)
        for path, body in (("/api/study-sessions", {"started_at": "2026-10-05T00:00:00Z"}),
                           ("/api/study-tasks", {"title": "Reading", "scheduled_event_id": str(ID)})):
            self.assertEqual((await self.client.post(path, json=body)).status_code, 422)
        response = await self.client.get("/api/study-events", params={"start_at": "2026-10-05T00:00:00", "end_at": "2026-10-06T00:00:00Z"})
        self.assertEqual(response.status_code, 422)
        self.assertEqual((await self.client.patch(f"/api/study-events/{ID}", json={"title": None})).status_code, 422)


if __name__ == "__main__":
    unittest.main()
