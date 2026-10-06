"""Narrow endpoint checks using mocked Auth and database boundaries, not live Supabase."""

import unittest
from unittest.mock import patch

import httpx

from app.core.config import Settings, get_settings
from app.main import app

USER_ID = "00000000-0000-4000-8000-000000000099"


class AuthFoundationChecks(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")
        self.settings = Settings(
            _env_file=None,
            supabase_url="https://project.example",
            supabase_service_role_key="test-only-key",
        )
        app.dependency_overrides[get_settings] = lambda: self.settings
        self.real_client = httpx.AsyncClient

    async def asyncTearDown(self):
        app.dependency_overrides.clear()
        await self.client.aclose()

    def mock_auth(self, handler):
        return patch("app.core.auth.httpx.AsyncClient", side_effect=lambda **kwargs: self.real_client(
            **kwargs, transport=httpx.MockTransport(handler)
        ))

    async def test_public_health_and_missing_or_wrong_scheme_token(self):
        response = await self.client.get("/health")
        self.assertEqual(response.json(), {"status": "ok"})
        for path in ("/api/auth/me", "/api/subjects"):
            for headers in ({}, {"Authorization": "Basic invalid"}):
                response = await self.client.get(path, headers=headers)
                self.assertEqual(response.status_code, 401)
                self.assertEqual(response.headers["WWW-Authenticate"], "Bearer")

    async def test_verified_user_comes_from_auth_service(self):
        def handler(request):
            self.assertEqual(request.url.path, "/auth/v1/user")
            self.assertEqual(request.headers["Authorization"], "Bearer test-token")
            self.assertEqual(request.headers["apikey"], "test-only-key")
            return httpx.Response(200, json={"id": USER_ID, "email": "reviewer@example.com", "role": "authenticated"})

        with self.mock_auth(handler):
            response = await self.client.get("/api/auth/me?user_id=untrusted", headers={"Authorization": "Bearer test-token"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"id": USER_ID, "email": "reviewer@example.com"})

    async def test_invalid_tokens_do_not_access_database(self):
        with self.mock_auth(lambda request: httpx.Response(401)), patch("app.api.subjects.list_subjects") as repository:
            for path in ("/api/auth/me", "/api/subjects"):
                response = await self.client.get(path, headers={"Authorization": "Bearer invalid-token"})
                self.assertEqual(response.status_code, 401)
            repository.assert_not_called()

    async def test_missing_configuration_returns_service_unavailable(self):
        self.settings.supabase_url = ""
        response = await self.client.get("/api/auth/me", headers={"Authorization": "Bearer test-token"})
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("test-token", response.text)

    async def test_auth_unavailable_or_malformed_response(self):
        for auth_response in (httpx.Response(500), httpx.Response(200, json={"id": "invalid"})):
            with self.mock_auth(lambda request: auth_response):
                response = await self.client.get("/api/auth/me", headers={"Authorization": "Bearer test-token"})
                self.assertEqual(response.status_code, 503)

        def timeout(request):
            raise httpx.ConnectTimeout("private diagnostic")

        with self.mock_auth(timeout):
            response = await self.client.get("/api/auth/me", headers={"Authorization": "Bearer test-token"})
            self.assertEqual(response.status_code, 503)
            self.assertNotIn("private diagnostic", response.text)

    async def test_database_failure_is_sanitized(self):
        with self.mock_auth(lambda request: httpx.Response(200, json={"id": USER_ID})), patch(
            "app.api.subjects.list_subjects", side_effect=ValueError("private connection detail")
        ):
            response = await self.client.get("/api/subjects", headers={"Authorization": "Bearer test-token"})
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("private connection detail", response.text)

    async def test_verified_subjects_read_and_no_write_routes(self):
        with self.mock_auth(lambda request: httpx.Response(200, json={"id": USER_ID})), patch(
            "app.api.subjects.list_subjects", return_value=[]
        ) as repository:
            response = await self.client.get("/api/subjects", headers={"Authorization": "Bearer test-token"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
        repository.assert_called_once()
        self.assertEqual((await self.client.post("/api/subjects")).status_code, 405)


if __name__ == "__main__":
    unittest.main()
