"""Focused Analytics profile dates, canonical plans, ownership and API checks."""
import unittest
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from unittest.mock import patch
from uuid import UUID

import httpx
from fastapi import FastAPI
from sqlalchemy.exc import SQLAlchemyError

from app.api.analytics import router
from app.core.auth import get_current_user
from app.schemas.auth import AuthenticatedUser
from app.services.analytics import analytics_range, day_windows, get_summary, local_day_range, planned_seconds
from app.services.planner_recurrence import PlannerError

USER = UUID("00000000-0000-4000-8000-000000000001")
FAR = UUID("00000000-0000-4000-8000-000000000101")
AFAR = UUID("00000000-0000-4000-8000-000000000102")
EVENT = UUID("00000000-0000-4000-8000-000000000301")
NOW = datetime(2026, 10, 9, 17, tzinfo=timezone.utc)


@contextmanager
def snapshot():
    yield object()


def event(**changes):
    return dict(id=EVENT, subject_id=FAR, topic_id=None, title="Read", event_type="reading",
                status="scheduled", start_at=datetime(2026, 10, 5, 1, tzinfo=timezone.utc),
                end_at=datetime(2026, 10, 5, 2, tzinfo=timezone.utc), timezone="Asia/Manila",
                recurrence_rule="FREQ=WEEKLY;BYDAY=MO,WE,FR", notes=None, created_at=NOW, updated_at=NOW) | changes


class AnalyticsDates(unittest.TestCase):
    def test_profile_local_inclusive_period_and_all_preset_sizes(self):
        for period in (7, 30, 90):
            start_day, end_day, start, end = analytics_range("Asia/Manila", period, now=NOW)
            self.assertEqual(end_day, date(2026, 10, 10))
            self.assertEqual((end_day - start_day).days + 1, period)
            self.assertEqual(start.hour, 16)
            self.assertEqual(end, datetime(2026, 10, 10, 16, tzinfo=timezone.utc))

    def test_dst_day_windows_preserve_23_and_25_hours(self):
        for day, hours in ((date(2026, 3, 8), 23), (date(2026, 11, 1), 25)):
            start, end = local_day_range(day, "America/New_York")
            self.assertEqual((end - start).total_seconds(), hours * 3600)
            windows = day_windows(day - timedelta(days=1), day + timedelta(days=1), "America/New_York")
            self.assertEqual(windows[0][2], windows[1][1])
            self.assertEqual(windows[1][2], windows[2][1])

    def test_midnight_fold_gap_and_skipped_calendar_date(self):
        cases = ((date(2026, 11, 1), "America/Havana", 25),
                 (date(2026, 9, 6), "America/Santiago", 23),
                 (date(2011, 12, 30), "Pacific/Apia", 0))
        for day, zone, hours in cases:
            start, end = local_day_range(day, zone)
            self.assertEqual((end - start).total_seconds(), hours * 3600)
            windows = day_windows(day - timedelta(days=1), day + timedelta(days=1), zone)
            self.assertEqual(windows[0][2], windows[1][1])
            self.assertEqual(windows[1][2], windows[2][1])
        start, end = local_day_range(date(2011, 12, 30), "Pacific/Apia")
        self.assertEqual(planned_seconds([], [], start, end), {})

    def test_custom_range_rejects_partial_reversed_long_future_and_overflow(self):
        for start, end in ((date(2026, 10, 1), None), (None, date(2026, 10, 1)),
                           (date(2026, 10, 2), date(2026, 10, 1)),
                           (date(2026, 7, 1), date(2026, 10, 1)),
                           (date(2026, 10, 1), date(2026, 10, 11))):
            with self.assertRaises(PlannerError):
                analytics_range("Asia/Manila", start_date=start, end_date=end, now=NOW)
        with self.assertRaises(PlannerError):
            local_day_range(date.max, "UTC")
        with self.assertRaises(PlannerError):
            local_day_range(date.min, "Asia/Taipei")
        with self.assertRaises(PlannerError):
            analytics_range("UTC", 90, now=datetime.min.replace(tzinfo=timezone.utc))
        # Exactly 90 inclusive days is allowed.
        start = date(2026, 10, 10) - timedelta(days=89)
        self.assertEqual(analytics_range("Asia/Manila", start_date=start,
                                        end_date=date(2026, 10, 10), now=NOW)[0], start)

    def test_profile_zone_can_make_same_instant_different_local_dates(self):
        self.assertEqual(analytics_range("America/New_York", now=NOW)[1], date(2026, 10, 9))
        self.assertEqual(analytics_range("Asia/Manila", now=NOW)[1], date(2026, 10, 10))
        with self.assertRaises(PlannerError):
            analytics_range("Not/AZone", now=NOW)


class PlannedStudy(unittest.TestCase):
    def test_recurrence_edited_subject_reschedule_deletion_and_cancelled(self):
        template = event()
        skipped = {key: template[key] for key in ("subject_id", "topic_id", "title", "event_type", "start_at", "end_at", "status", "notes", "created_at", "updated_at")}
        skipped.update(id=UUID("00000000-0000-4000-8000-000000000401"), study_event_id=EVENT,
                       occurrence_date=date(2026, 10, 7), is_deleted=False, subject_id=AFAR, status="skipped",
                       start_at=datetime(2026, 10, 8, 1, tzinfo=timezone.utc), end_at=datetime(2026, 10, 8, 3, tzinfo=timezone.utc))
        deleted = skipped | {"id": UUID("00000000-0000-4000-8000-000000000402"),
                             "occurrence_date": date(2026, 10, 9), "is_deleted": True}
        cancelled = event(id=UUID("00000000-0000-4000-8000-000000000302"), recurrence_rule=None, status="cancelled")
        start, _ = local_day_range(date(2026, 10, 5), "Asia/Manila")
        _, end = local_day_range(date(2026, 10, 9), "Asia/Manila")
        self.assertEqual(planned_seconds([template, cancelled], [skipped, deleted], start, end),
                         {FAR: 3600, AFAR: 7200})

    def test_clipped_multiday_oneoff_and_completed_plan_count_once(self):
        template = event(recurrence_rule=None, status="completed", subject_id=None,
                         start_at=datetime(2026, 10, 4, 12, tzinfo=timezone.utc),
                         end_at=datetime(2026, 10, 8, 12, tzinfo=timezone.utc))
        start, _ = local_day_range(date(2026, 10, 5), "UTC")
        _, end = local_day_range(date(2026, 10, 6), "UTC")
        self.assertEqual(planned_seconds([template], [], start, end), {None: 48 * 3600})


class SummaryComposition(unittest.TestCase):
    def test_planned_only_subject_and_unassigned_remain_independent(self):
        rows = [{"subject_id": FAR, "subject_code": "FAR", "subject_title": "Financial Accounting",
                 "duration_seconds": 900, "session_count": 2},
                {"subject_id": None, "subject_code": None, "subject_title": None,
                 "duration_seconds": 300, "session_count": 1}]
        daily = [{"date": date(2026, 10, 9), "duration_seconds": 1200, "session_count": 3},
                 {"date": date(2026, 10, 10), "duration_seconds": 0, "session_count": 0}]
        with patch("app.repositories.analytics.snapshot", snapshot), \
             patch("app.repositories.planner.profile_timezone", return_value="Asia/Manila"), \
             patch("app.repositories.analytics.aggregate_sessions", return_value={"total_seconds": 1200, "session_count": 3,
                                                                                   "average_session_seconds": 400, "longest_session_seconds": 750}), \
             patch("app.repositories.analytics.daily_sessions", return_value=daily), \
             patch("app.repositories.analytics.session_breakdowns", return_value=(rows, [{"activity_type": "reading", "duration_seconds": 1200, "session_count": 3}])), \
             patch("app.repositories.planner.event_range", return_value=([event(subject_id=AFAR, recurrence_rule=None,
                 start_at=datetime(2026, 10, 9, 1, tzinfo=timezone.utc), end_at=datetime(2026, 10, 9, 2, tzinfo=timezone.utc))], [])), \
             patch("app.repositories.analytics.subject_labels", return_value={AFAR: ("AFAR", "Advanced Accounting", "indigo")}):
            data = get_summary(USER, start_date=date(2026, 10, 9), end_date=date(2026, 10, 10), now=NOW)
        self.assertEqual(data.summary.total_seconds, 1200)
        self.assertEqual(data.summary.planned_seconds, 3600)
        self.assertEqual(data.summary.active_days, 1)
        self.assertEqual(data.summary.average_session_seconds, 400)
        self.assertEqual(data.summary.longest_session_seconds, 750)
        self.assertEqual(sum(row.duration_seconds for row in data.subjects), 1200)
        by_subject = {row.subject_id: row for row in data.subjects}
        self.assertEqual(by_subject[AFAR].duration_seconds, 0)
        self.assertEqual(by_subject[AFAR].subject_color_key, "indigo")
        self.assertEqual(by_subject[FAR].planned_seconds, 0)
        self.assertEqual(by_subject[None].duration_seconds, 300)


class SQLScope(unittest.TestCase):
    def test_database_aggregates_not_truncated_session_list(self):
        from app.repositories import analytics as repo

        class Connection:
            def __init__(self):
                self.queries = []
            def execute(self, query, params):
                self.queries.append((str(query), params.copy()))
                return self
            def mappings(self):
                return self
            def one(self):
                return {"total_seconds": 0, "session_count": 0, "average_session_seconds": 0, "longest_session_seconds": 0}
            def scalar_one(self):
                return 0
            def __iter__(self):
                return iter([])

        connection = Connection()
        start, end = local_day_range(date(2026, 10, 9), "UTC")
        repo.aggregate_sessions(connection, USER, start, end)
        repo.daily_sessions(connection, USER, [(date(2026, 10, 9), start, end)])
        repo.session_breakdowns(connection, USER, start, end)
        for query, params in connection.queries:
            self.assertEqual(params["user_id"], USER)
            self.assertIn("user_id = :user_id", query)
            self.assertIn("ended_at IS NOT NULL", query)
            self.assertIn("started_at < :end_at AND ended_at > :start_at", query)
            self.assertNotIn("LIMIT", query)
            self.assertIn("FLOOR(EXTRACT(EPOCH FROM", query)
        history = repo.list_labeled_sessions(connection, USER, start, end, limit=20, offset=100)
        self.assertEqual(history, {"sessions": [], "total": 0, "limit": 20, "offset": 100})
        query, params = connection.queries[-1]
        self.assertIn("ss.user_id = :user_id", query)
        self.assertIn("ss.ended_at IS NOT NULL", query)
        self.assertIn("LIMIT :limit OFFSET :offset", query)
        self.assertIn("ss.started_at DESC, ss.id DESC", query)
        self.assertIn("s.code AS subject_code", query)
        self.assertEqual(params["offset"], 100)


class AnalyticsAPI(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.app = FastAPI()
        self.app.include_router(router)
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app), base_url="http://test")

    async def asyncTearDown(self):
        await self.client.aclose()

    async def test_requires_authentication(self):
        for path in ("summary", "sessions"):
            self.assertEqual((await self.client.get(f"/api/analytics/{path}")).status_code, 401)

    async def test_invalid_query_and_ranges_return_422(self):
        self.app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id=USER, email=None)
        for query in ("period=8", "period=not-a-number", "limit=101", "limit=0", "offset=-1", "start_date=not-a-date"):
            response = await self.client.get("/api/analytics/sessions?" + query)
            self.assertEqual(response.status_code, 422, response.text)
        with patch("app.repositories.analytics.snapshot", snapshot), \
             patch("app.repositories.planner.profile_timezone", return_value="UTC"):
            for query in ("start_date=2026-10-01", "end_date=2026-10-01", "start_date=2026-10-02&end_date=2026-10-01",
                          "start_date=2026-01-01&end_date=2026-10-01", "start_date=9999-12-31&end_date=9999-12-31"):
                response = await self.client.get("/api/analytics/summary?" + query)
                self.assertEqual(response.status_code, 422, response.text)

    async def test_supported_period_query_and_verified_owner_forwarded(self):
        self.app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id=USER, email=None)
        for period in (7, 30, 90):
            with patch("app.services.analytics.get_sessions", return_value={"sessions": [], "total": 0, "limit": 20, "offset": 0}) as call:
                response = await self.client.get(f"/api/analytics/sessions?period={period}")
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(call.call_args.args[0], USER)
            self.assertEqual(call.call_args.args[1], period)

    async def test_dependency_failure_is_sanitized(self):
        self.app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id=USER, email=None)
        with patch("app.services.analytics.get_summary", side_effect=SQLAlchemyError("private DSN and content")):
            response = await self.client.get("/api/analytics/summary")
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("private DSN", response.text)


if __name__ == "__main__":
    unittest.main()
