"""Focused Phase 9 dashboard recall counts; no external data or writes."""
import unittest
from unittest.mock import patch

from tests.test_dashboard import USER, NOW, snapshot


class RecallDashboardChecks(unittest.TestCase):
    def test_dashboard_reuses_current_owner_and_local_day_for_recall_counts(self):
        from app.services.dashboard import get_dashboard, today_range
        with patch('app.repositories.dashboard.snapshot', snapshot), \
             patch('app.repositories.planner.profile_timezone', return_value='Asia/Manila'), \
             patch('app.repositories.dashboard.subject_counts', return_value=[]), \
             patch('app.repositories.planner.event_range', return_value=([], [])), \
             patch('app.repositories.dashboard.pending_tasks', return_value=[]), \
             patch('app.repositories.dashboard.curriculum_labels', return_value=({}, {})), \
             patch('app.repositories.dashboard.recall_counts', create=True, return_value={'overdue': 2, 'due_today': 3}) as counts:
            result = get_dashboard(USER, now=NOW)
        self.assertEqual(result.recall_summary.overdue, 2)
        self.assertEqual(result.recall_summary.due_today, 3)
        counts.assert_called_once_with(unittest.mock.ANY, USER, today_range(NOW, 'Asia/Manila')[1], NOW)

    def test_recall_count_query_limits_to_owned_active_currently_due_cards(self):
        from app.repositories.dashboard import recall_counts
        class Connection:
            def execute(self, query, params):
                self.sql, self.params = str(query), params
                return self
            def mappings(self): return self
            def one(self): return {'overdue': 0, 'due_today': 0}
        connection = Connection()
        self.assertEqual(recall_counts(connection, USER, NOW, NOW), {'overdue': 0, 'due_today': 0})
        self.assertEqual(connection.params['user_id'], USER)
        for fragment in ('user_id = :user_id', "status = 'active'", 'next_review_at <= :now', 'next_review_at < :start'):
            self.assertIn(fragment, connection.sql)
