"""Focused timer contracts, ownership and profile-local read boundaries."""
import unittest
from contextlib import ExitStack, nullcontext
from datetime import datetime, timezone
from uuid import UUID
from unittest.mock import patch

import httpx
from fastapi import FastAPI
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.api import focus as focus_api, planner as planner_api
from app.core.auth import get_current_user
from app.schemas.auth import AuthenticatedUser
from app.schemas.planner import SessionCreate, SessionPatch
from app.services import focus, planner
from app.services.planner_recurrence import PlannerError

OWNER = UUID(int=1)
SESSION = UUID(int=2)
NOW = datetime(2026, 10, 9, 12, tzinfo=timezone.utc)


def session(**changes):
    return {
        "id": SESSION, "study_event_id": None, "occurrence_id": None,
        "subject_id": None, "topic_id": None, "activity_type": "general",
        "started_at": NOW, "ended_at": None, "duration_seconds": None,
        "notes": None, "created_at": NOW, **changes,
    }


class SessionActivityChecks(unittest.TestCase):
    def test_activity_values_and_default(self):
        self.assertEqual(SessionCreate().activity_type, "general")
        for activity in ("lecture", "reading", "practice", "recall", "quiz", "general"):
            self.assertEqual(SessionCreate(activity_type=activity).activity_type, activity)
        for activity in ("drill", "assessment", "", None):
            with self.subTest(activity=activity), self.assertRaises(ValidationError):
                SessionCreate(activity_type=activity)

    def test_client_cannot_assign_owner_time_duration_or_patch_activity(self):
        for field, value in (("user_id", str(OWNER)), ("started_at", NOW.isoformat()),
                             ("ended_at", NOW.isoformat()), ("duration_seconds", 1)):
            with self.subTest(field=field), self.assertRaises(ValidationError):
                SessionCreate(**{field: value})
        with self.assertRaises(ValidationError):
            SessionPatch(action="stop", activity_type="reading")

    def test_create_persists_selected_activity_with_verified_owner(self):
        connection = object()
        for activity in ("general", "reading"):
            body = SessionCreate() if activity == "general" else SessionCreate(activity_type=activity)
            with patch.object(planner.repo, "transaction", return_value=nullcontext(connection)), \
                 patch.object(planner.repo, "active_session", return_value=None) as active, \
                 patch.object(planner.repo, "valid_associations", return_value=True), \
                 patch.object(planner.repo, "insert_record", side_effect=lambda c, k, u, d: d) as insert:
                result = planner.create_session(OWNER, body)
            active.assert_called_once_with(connection, OWNER)
            self.assertEqual(result["activity_type"], activity)
            self.assertNotIn("duration_seconds", result)
            self.assertEqual(insert.call_args.args[:3], (connection, "sessions", OWNER))

    def test_conflicting_start_does_not_insert(self):
        with patch.object(planner.repo, "transaction", return_value=nullcontext(object())), \
             patch.object(planner.repo, "active_session", return_value=session()), \
             patch.object(planner.repo, "insert_record") as insert:
            with self.assertRaises(PlannerError) as error:
                planner.create_session(OWNER, SessionCreate(activity_type="practice"))
            self.assertEqual(error.exception.status_code, 409)
            insert.assert_not_called()

    def test_foreign_or_missing_session_cannot_be_stopped(self):
        connection = object()
        with patch.object(planner.repo, "transaction", return_value=nullcontext(connection)), \
             patch.object(planner.repo, "get_record", return_value=None) as lookup, \
             patch.object(planner.repo, "stop_session") as stop:
            with self.assertRaises(PlannerError) as error:
                planner.patch_session(OWNER, SESSION, SessionPatch(action="stop"))
            self.assertEqual(error.exception.status_code, 404)
            lookup.assert_called_once_with(connection, "sessions", OWNER, SESSION, lock=True)
            stop.assert_not_called()


class FocusReadChecks(unittest.TestCase):
    def read(self, *, zone="Asia/Taipei", now=NOW, active=None, recent=None):
        connection = object()
        with ExitStack() as stack:
            stack.enter_context(patch.object(focus.analytics_repo, "snapshot", return_value=nullcontext(connection)))
            profile = stack.enter_context(patch.object(focus.repo, "profile_timezone", return_value=zone))
            active_lookup = stack.enter_context(patch.object(focus.repo, "active_session", return_value=active))
            aggregate = stack.enter_context(patch.object(focus.analytics_repo, "aggregate_sessions", return_value={"total_seconds": 600, "session_count": 2}))
            history = stack.enter_context(patch.object(focus.analytics_repo, "list_labeled_sessions", return_value={"sessions": recent or []}))
            result = focus.get_focus(OWNER, now=now)
        profile.assert_called_once_with(connection, OWNER)
        active_lookup.assert_called_once_with(connection, OWNER)
        history.assert_called_once_with(connection, OWNER, limit=10)
        self.assertEqual(aggregate.call_args.args[:2], (connection, OWNER))
        return result, aggregate.call_args.args[2:]

    def test_restores_active_and_returns_separate_completed_totals(self):
        completed = session(ended_at=NOW, duration_seconds=600, subject_code="FAR",
                            subject_title="Financial Accounting", topic_title="Assets", user_id=OWNER)
        result, bounds = self.read(active=session(activity_type="practice"), recent=[completed])
        self.assertEqual(result.server_now, NOW)
        self.assertEqual(result.active_session.activity_type, "practice")
        self.assertEqual((result.today_seconds, result.today_session_count), (600, 2))
        self.assertEqual(result.recent_sessions[0].subject_title, "Financial Accounting")
        self.assertNotIn("user_id", result.model_dump()["recent_sessions"][0])
        self.assertEqual(bounds, (datetime(2026, 10, 8, 16, tzinfo=timezone.utc),
                                  datetime(2026, 10, 9, 16, tzinfo=timezone.utc)))

    def test_local_midnight_and_dst_day_bounds(self):
        for now, hours, start in (
            (datetime(2026, 3, 8, 12, tzinfo=timezone.utc), 23, datetime(2026, 3, 8, 5, tzinfo=timezone.utc)),
            (datetime(2026, 11, 1, 12, tzinfo=timezone.utc), 25, datetime(2026, 11, 1, 4, tzinfo=timezone.utc)),
        ):
            with self.subTest(now=now):
                result, bounds = self.read(zone="America/New_York", now=now)
                self.assertIsNone(result.active_session)
                self.assertEqual(bounds[0], start)
                self.assertEqual((bounds[1] - bounds[0]).total_seconds(), hours * 3600)

    def test_response_enforces_ten_recent_sessions(self):
        with self.assertRaises(ValidationError):
            self.read(recent=[session(subject_code=None, subject_title=None, topic_title=None)] * 11)


class FocusApiChecks(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.app = FastAPI()
        self.app.include_router(focus_api.router)
        self.app.include_router(planner_api.router)
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app), base_url="http://test")

    async def asyncTearDown(self):
        await self.client.aclose()

    def authenticate(self):
        self.app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id=OWNER, email=None)

    async def test_focus_requires_authentication(self):
        self.assertEqual((await self.client.get("/api/focus")).status_code, 401)

    async def test_identity_is_verified_and_infrastructure_errors_are_sanitized(self):
        self.authenticate()
        with patch.object(focus_api.service, "get_focus", side_effect=SQLAlchemyError("private detail")) as read:
            response = await self.client.get("/api/focus")
        read.assert_called_once_with(OWNER)
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("private detail", response.text)

    async def test_invalid_activity_owner_and_duration_fail_before_session_mutation(self):
        self.authenticate()
        with patch.object(planner_api.service, "create_session") as create:
            for body in ({"activity_type": "drill"}, {"activity_type": None},
                         {"user_id": str(OWNER)}, {"duration_seconds": 600}):
                with self.subTest(body=body):
                    self.assertEqual((await self.client.post("/api/study-sessions", json=body)).status_code, 422)
            create.assert_not_called()


if __name__ == "__main__":
    unittest.main()
