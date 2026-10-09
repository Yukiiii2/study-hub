"""Narrow read-only dashboard auth, aggregation and date-boundary checks."""
import unittest
from contextlib import contextmanager
from datetime import date, datetime, timezone
from unittest.mock import patch
from uuid import UUID

import httpx
from sqlalchemy.exc import SQLAlchemyError

from app.main import app
from app.core.auth import get_current_user
from app.schemas.auth import AuthenticatedUser

USER = UUID("00000000-0000-4000-8000-000000000001")
FAR = UUID("00000000-0000-4000-8000-000000000101")
AFAR = UUID("00000000-0000-4000-8000-000000000102")
TOPIC = UUID("00000000-0000-4000-8000-000000000201")
NOW = datetime(2026, 10, 6, 17, tzinfo=timezone.utc)


def subject_rows():
    return [
        dict(id=FAR, code="FAR", name="Financial Accounting and Reporting", display_order=1, color_key="blue",
             topic_count=3, video_count=4, completed_video_count=2, total_duration_seconds=150,
             completed_duration_seconds=60, unknown_duration_videos=1, in_progress_videos=0),
        dict(id=AFAR, code="AFAR", name="Advanced Financial Accounting and Reporting", display_order=2, color_key="indigo",
             topic_count=2, video_count=2, completed_video_count=1, total_duration_seconds=60,
             completed_duration_seconds=40, unknown_duration_videos=0, in_progress_videos=1),
    ]


def recurring_event():
    return dict(id=UUID("00000000-0000-4000-8000-000000000301"), subject_id=FAR, topic_id=TOPIC,
                title="Read the curriculum", event_type="reading", status="scheduled",
                start_at=datetime(2026, 10, 5, 1, tzinfo=timezone.utc),
                end_at=datetime(2026, 10, 5, 2, tzinfo=timezone.utc), timezone="Asia/Manila",
                recurrence_rule="FREQ=WEEKLY;BYDAY=MO,WE", notes=None, created_at=NOW, updated_at=NOW)


@contextmanager
def snapshot():
    yield object()


class DashboardDataChecks(unittest.TestCase):
    def test_profile_timezone_day_boundaries_and_dst(self):
        from app.services.dashboard import today_range
        day, start, end = today_range(NOW, "Asia/Manila")
        self.assertEqual(day, date(2026, 10, 7))
        self.assertEqual(start, datetime(2026, 10, 6, 16, tzinfo=timezone.utc))
        self.assertEqual(end, datetime(2026, 10, 7, 16, tzinfo=timezone.utc))
        _, start, end = today_range(datetime(2026, 3, 8, 12, tzinfo=timezone.utc), "America/New_York")
        self.assertEqual((end - start).total_seconds(), 23 * 3600)
        _, start, end = today_range(datetime(2026, 11, 1, 12, tzinfo=timezone.utc), "America/New_York")
        self.assertEqual((end - start).total_seconds(), 25 * 3600)

    def test_real_counts_known_duration_totals_and_recurring_today(self):
        from app.services.dashboard import get_dashboard
        with patch("app.repositories.dashboard.snapshot", snapshot), \
             patch("app.repositories.planner.profile_timezone", return_value="Asia/Manila"), \
             patch("app.repositories.dashboard.subject_counts", return_value=subject_rows()), \
             patch("app.repositories.planner.event_range", return_value=([recurring_event()], [])), \
             patch("app.repositories.dashboard.pending_tasks", return_value=[]), \
             patch("app.repositories.dashboard.recall_counts", return_value={"overdue": 0, "due_today": 0}), \
             patch("app.repositories.dashboard.curriculum_labels", return_value=({FAR: "FAR"}, {TOPIC: "Real source topic"})):
            data = get_dashboard(USER, now=NOW)
        self.assertEqual(data.video_summary.total_videos, 6)
        self.assertEqual(data.video_summary.completed_videos, 3)
        self.assertEqual(data.video_summary.remaining_videos, 3)
        self.assertEqual(data.video_summary.total_duration_seconds, 210)
        self.assertEqual(data.video_summary.completed_duration_seconds, 100)
        self.assertEqual(data.video_summary.remaining_duration_seconds, 110)
        self.assertEqual(data.video_summary.unknown_duration_videos, 1)
        self.assertEqual([s.topic_count for s in data.subjects], [3, 2])
        self.assertEqual(data.continue_video_subject_id, AFAR)
        self.assertEqual(len(data.today_events), 1)
        event = data.today_events[0]
        self.assertEqual(event.occurrence_date, date(2026, 10, 7))
        self.assertEqual(event.start_at, datetime(2026, 10, 7, 1, tzinfo=timezone.utc))
        self.assertEqual(event.subject_code, "FAR")
        self.assertEqual(event.topic_title, "Real source topic")

    def test_empty_data_remains_empty_without_manufacturing_activity(self):
        from app.services.dashboard import get_dashboard
        with patch("app.repositories.dashboard.snapshot", snapshot), \
             patch("app.repositories.planner.profile_timezone", return_value="Asia/Manila"), \
             patch("app.repositories.dashboard.subject_counts", return_value=[]), \
             patch("app.repositories.planner.event_range", return_value=([], [])), \
             patch("app.repositories.dashboard.pending_tasks", return_value=[]), \
             patch("app.repositories.dashboard.recall_counts", return_value={"overdue": 0, "due_today": 0}), \
             patch("app.repositories.dashboard.curriculum_labels", return_value=({}, {})):
            data = get_dashboard(USER, now=NOW)
        self.assertEqual(data.today_events, [])
        self.assertEqual(data.upcoming_tasks, [])
        self.assertEqual(data.video_summary.total_videos, 0)
        self.assertEqual(data.video_summary.remaining_duration_seconds, 0)
        self.assertIsNone(data.continue_video_subject_id)

    def test_repository_queries_bind_owner_and_bound_pending_results(self):
        from app.repositories.dashboard import subject_counts, pending_tasks
        class RecordingConnection:
            def execute(self, query, params):
                self.query, self.params = str(query), params
                return self
            def mappings(self):
                return []
        connection = RecordingConnection()
        subject_counts(connection, USER)
        self.assertEqual(connection.params["user_id"], USER)
        self.assertIn("p.user_id = :user_id", connection.query)
        self.assertIn("s.is_active", connection.query)
        pending_tasks(connection, USER)
        self.assertEqual(connection.params["user_id"], USER)
        self.assertIn("user_id = :user_id", connection.query)
        self.assertIn("status = 'pending'", connection.query)
        self.assertIn("due_at ASC NULLS LAST", connection.query)
        self.assertIn("LIMIT 5", connection.query)


class DashboardAuthChecks(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")

    async def asyncTearDown(self):
        app.dependency_overrides.clear()
        await self.client.aclose()

    async def test_dashboard_requires_authentication(self):
        response = await self.client.get("/api/dashboard")
        self.assertEqual(response.status_code, 401)

    async def test_database_failures_are_sanitized(self):
        app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id=USER, email=None)
        with patch("app.api.dashboard.get_dashboard", side_effect=SQLAlchemyError("private connection details")):
            response = await self.client.get("/api/dashboard")
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("private connection details", response.text)


if __name__ == "__main__":
    unittest.main()
