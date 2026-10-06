"""Focused authentication and progress validation boundary checks."""
import unittest
from unittest.mock import patch
from uuid import UUID
import httpx
from app.main import app
from app.core.auth import get_current_user
from app.schemas.auth import AuthenticatedUser

ID = "00000000-0000-4000-8000-000000000001"


class VideoApiChecks(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")

    async def asyncTearDown(self):
        app.dependency_overrides.clear()
        await self.client.aclose()

    async def test_video_routes_require_authentication(self):
        for path in (f"/api/subjects/{ID}/videos", f"/api/topics/{ID}/videos"):
            self.assertEqual((await self.client.get(path)).status_code, 401)
        self.assertEqual((await self.client.patch(f"/api/videos/{ID}/progress", json={"status": "completed"})).status_code, 401)

    async def test_progress_rejects_invalid_status_and_supplied_identity(self):
        app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id=UUID(ID), email=None)
        for body in ({"status": "invented"}, {"status": "completed", "user_id": ID}):
            self.assertEqual((await self.client.patch(f"/api/videos/{ID}/progress", json=body)).status_code, 422)
        with patch("app.api.videos.update_progress", return_value=None) as update:
            response = await self.client.patch(f"/api/videos/{ID}/progress", json={"status": "completed"})
            self.assertEqual(response.status_code, 404)
            self.assertEqual(update.call_args.args[1], UUID(ID))


if __name__ == "__main__":
    unittest.main()
