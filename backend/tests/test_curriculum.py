"""Narrow Phase 3 read endpoint checks; no live database writes."""
import unittest
from unittest.mock import patch
from uuid import UUID

import httpx

from app.main import app
from app.core.auth import get_current_user
from app.schemas.auth import AuthenticatedUser

ID = "00000000-0000-4000-8000-000000000001"


class CurriculumChecks(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")

    async def asyncTearDown(self):
        app.dependency_overrides.clear()
        await self.client.aclose()

    async def test_detail_routes_require_authentication(self):
        for path in (f"/api/subjects/{ID}", f"/api/subjects/{ID}/topics", f"/api/topics/{ID}"):
            self.assertEqual((await self.client.get(path)).status_code, 401)

    async def test_unknown_records_return_not_found(self):
        app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id=UUID(ID), email=None)
        with patch("app.api.subjects.get_subject", return_value=None):
            for path in (f"/api/subjects/{ID}", f"/api/subjects/{ID}/topics"):
                self.assertEqual((await self.client.get(path)).status_code, 404)
        with patch("app.api.topics.get_topic", return_value=None):
            self.assertEqual((await self.client.get(f"/api/topics/{ID}")).status_code, 404)


if __name__ == "__main__":
    unittest.main()

