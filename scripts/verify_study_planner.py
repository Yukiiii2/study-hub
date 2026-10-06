"""Explicit, narrow live planner verification; deletes only accounts it creates."""
import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import secrets
import sys
from uuid import uuid4
from zoneinfo import ZoneInfo

import httpx
from dotenv import dotenv_values
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.db.connection import get_engine  # noqa: E402


def request(client, method, path, status=200, **kwargs):
    response = client.request(method, path, **kwargs)
    assert response.status_code == status, f"{method} planner request expected {status}, received {response.status_code}"
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3001"
    return response.json() if response.status_code != 204 else None


def check_rls(users):
    tables = ("study_events", "study_event_occurrences", "study_tasks", "study_sessions")
    with get_engine().connect() as db:
        for user_id in users:
            with db.begin():
                db.execute(text("SET LOCAL ROLE authenticated"))
                db.execute(text("SELECT set_config('request.jwt.claims', :claims, true)"),
                           {"claims": json.dumps({"sub": user_id, "role": "authenticated"})})
                for table in tables:
                    assert db.execute(text(f"SELECT count(*) FROM public.{table} WHERE user_id <> :owner"), {"owner": user_id}).scalar() == 0
                try:
                    with db.begin_nested():
                        db.execute(text("INSERT INTO public.study_tasks(user_id,title) VALUES (:owner,'Verification write must be denied')"), {"owner": user_id})
                        raise AssertionError("Browser mutation grant was unexpectedly present")
                except DBAPIError as error:
                    assert getattr(error.orig, "sqlstate", None) == "42501"
    print("PASS: four-table RLS read isolation and browser write rejection", flush=True)


def verify(api_url):
    backend = dotenv_values(ROOT / "backend/.env")
    frontend = dotenv_values(ROOT / "frontend/.env.local")
    assert frontend.get("NEXT_PUBLIC_API_URL") == api_url, "Frontend API URL must match the verification API"
    base = backend["SUPABASE_URL"].rstrip("/")
    secret_key = backend["SUPABASE_SECRET_KEY"]
    publishable = frontend["NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY"]
    users, clients = [], []
    cleaned = True
    with httpx.Client(timeout=20) as provider:
        try:
            for _ in range(2):
                email, password = f"study-hub-planner-verify-{uuid4().hex}@example.com", secrets.token_urlsafe(32)
                created = provider.post(base + "/auth/v1/admin/users", headers={"apikey": secret_key, "Authorization": "Bearer " + secret_key},
                                        json={"email": email, "password": password, "email_confirm": True})
                assert created.status_code in (200, 201), f"Temporary Auth user creation failed ({created.status_code})"
                users.append(created.json()["id"])
                login = provider.post(base + "/auth/v1/token", params={"grant_type": "password"}, headers={"apikey": publishable},
                                      json={"email": email, "password": password})
                assert login.status_code == 200, f"Temporary Auth sign-in failed ({login.status_code})"
                clients.append(httpx.Client(base_url=api_url, timeout=25, headers={"Origin": "http://localhost:3001", "Authorization": "Bearer " + login.json()["access_token"]}))
            a, b = clients
            assert request(a, "GET", "/health") == {"status": "ok"}
            assert request(a, "GET", "/api/auth/me")["id"] == users[0]
            context = request(a, "GET", "/api/study-plan/context")
            assert context["active_session"] is None
            subjects = request(a, "GET", "/api/subjects")
            topic = request(a, "GET", f"/api/subjects/{subjects[0]['id']}/topics")[0]
            other = subjects[1]["id"]
            zone = ZoneInfo(context["timezone"])
            start = (datetime.now(timezone.utc) + timedelta(days=1)).replace(hour=1, minute=0, second=0, microsecond=0)
            end = start + timedelta(minutes=45)
            payload = {"title": "Temporary planner verification", "subject_id": topic["subject_id"], "topic_id": topic["id"],
                       "event_type": "reading", "start_at": start.isoformat(), "end_at": end.isoformat(), "timezone": context["timezone"]}
            window = {"start_at": (start-timedelta(days=1)).isoformat(), "end_at": (start+timedelta(days=30)).isoformat()}
            event = request(a, "POST", "/api/study-events", 201, json=payload)
            path = f"/api/study-events/{event['id']}"
            request(a, "POST", "/api/study-events", 422, json={**payload, "subject_id": other})
            request(a, "POST", "/api/study-events", 422, json={**payload, "user_id": users[1]})
            request(a, "PATCH", path, 422, json={"end_at": (start-timedelta(minutes=1)).isoformat()})
            assert request(a, "GET", path)["end_at"] == event["end_at"]
            for method, body in (("GET", None), ("PATCH", {"title": "Forbidden"}), ("DELETE", None)):
                request(b, method, path, 404, **({"json": body} if body else {}))
            request(a, "GET", "/api/study-events", 422, params={**window, "end_at": (start+timedelta(days=94)).isoformat()})
            assert len(request(b, "GET", "/api/study-events", params=window)) == 0
            print("PASS: event CRUD, strict inputs, relationships, ranges and cross-user isolation", flush=True)

            session = request(a, "POST", "/api/study-sessions", 201, json={"study_event_id": event["id"]})
            session_path = f"/api/study-sessions/{session['id']}"
            request(a, "POST", "/api/study-sessions", 409, json={"study_event_id": event["id"]})
            request(b, "PATCH", session_path, 404, json={"action": "stop"})
            stopped = request(a, "PATCH", session_path, json={"action": "stop"})
            elapsed = int((datetime.fromisoformat(stopped["ended_at"]) - datetime.fromisoformat(stopped["started_at"])).total_seconds())
            assert stopped["duration_seconds"] == elapsed
            assert request(a, "PATCH", session_path, json={"action": "stop"})["ended_at"] == stopped["ended_at"]
            assert request(a, "GET", path)["end_at"] == event["end_at"]
            assert request(b, "GET", "/api/study-sessions") == []
            print("PASS: actual sessions, active-session conflict, stop idempotency and planned-time preservation", flush=True)

            day = start.astimezone(zone).date()
            weekday = ("MO", "TU", "WE", "TH", "FR", "SA", "SU")[day.weekday()]
            series = request(a, "POST", "/api/study-events", 201, json={**payload, "recurrence_rule": "FREQ=WEEKLY;BYDAY="+weekday})
            series_path = f"/api/study-events/{series['id']}"
            first = f"{series_path}/occurrences/{day.isoformat()}"
            changed = request(a, "PATCH", first, json={"status": "completed", "title": "Temporary occurrence edit"})
            assert changed["occurrence_id"] and changed["status"] == "completed"
            second_day = day+timedelta(days=7)
            second = f"{series_path}/occurrences/{second_day.isoformat()}"
            moved = request(a, "PATCH", second, json={"start_at": (start+timedelta(days=9)).isoformat(), "end_at": (end+timedelta(days=9)).isoformat()})
            move_range = {"start_at": (start+timedelta(days=8)).isoformat(), "end_at": (start+timedelta(days=10)).isoformat()}
            assert any(row["occurrence_id"] == moved["occurrence_id"] for row in request(a, "GET", "/api/study-events", params=move_range))
            removed_day = day+timedelta(days=14)
            request(a, "DELETE", f"{series_path}/occurrences/{removed_day.isoformat()}", 204)
            request(a, "PATCH", series_path, json={"title": "Temporary series edit"})
            occurrences = [row for row in request(a, "GET", "/api/study-events", params=window) if row["id"] == series["id"]]
            assert all(row["occurrence_date"] != removed_day.isoformat() for row in occurrences)
            assert any(row["title"] == "Temporary occurrence edit" for row in occurrences)
            request(a, "PATCH", series_path, 409, json={"timezone": "UTC"})
            request(a, "POST", "/api/study-events", 422, json={**payload, "recurrence_rule": "FREQ=DAILY"})
            series_session = request(a, "POST", "/api/study-sessions", 201, json={"study_event_id": series["id"], "occurrence_date": day.isoformat()})
            assert series_session["occurrence_id"] == changed["occurrence_id"]
            request(a, "PATCH", f"/api/study-sessions/{series_session['id']}", json={"action": "stop"})
            print("PASS: weekly recurrence, independent edits, moved-range inclusion, suppression and series snapshot preservation", flush=True)

            task = request(a, "POST", "/api/study-tasks", 201, json={"title": "Temporary task", "subject_id": topic["subject_id"], "topic_id": topic["id"], "estimated_minutes": 45})
            task_path = f"/api/study-tasks/{task['id']}"
            request(b, "PATCH", task_path, 404, json={"title": "Forbidden"})
            request(b, "DELETE", task_path, 404)
            request(a, "POST", task_path+"/schedule", 422, json={**payload, "subject_id": other})
            task_after_failure = next(row for row in request(a, "GET", "/api/study-tasks") if row["id"] == task["id"])
            assert task_after_failure["status"] == "pending" and task_after_failure["scheduled_event_id"] is None
            scheduled = request(a, "POST", task_path+"/schedule", 201, json=payload)
            request(a, "POST", task_path+"/schedule", 409, json=payload)
            request(a, "DELETE", f"/api/study-events/{scheduled['id']}", 204)
            assert next(row for row in request(a, "GET", "/api/study-tasks") if row["id"] == task["id"])["status"] == "pending"
            request(a, "PATCH", task_path, json={"status": "completed", "estimated_minutes": None})
            print("PASS: tasks, atomic scheduling, duplicate rejection and event-deletion unscheduling", flush=True)

            check_rls(users)
            # Database constraints independently reject forged ownership and topic references.
            with get_engine().connect() as db:
                for statement, params in [
                    ("INSERT INTO public.study_sessions(user_id,study_event_id) VALUES (:user_id,:event_id)", {"user_id":users[1],"event_id":event["id"]}),
                    ("INSERT INTO public.study_tasks(user_id,subject_id,topic_id,title) VALUES (:user_id,:subject_id,:topic_id,'Rejected mismatch')", {"user_id":users[0],"subject_id":other,"topic_id":topic["id"]}),
                ]:
                    tx = db.begin()
                    try:
                        db.execute(text(statement), params)
                    except DBAPIError as error:
                        assert getattr(error.orig,"sqlstate",None) == "23503"
                    else:
                        raise AssertionError("Forged relationship passed a database constraint")
                    finally:
                        tx.rollback()
            request(a, "DELETE", series_path, 204)
            remaining = request(a, "GET", "/api/study-sessions")
            detached = next(row for row in remaining if row["id"] == series_session["id"])
            assert detached["study_event_id"] is None and detached["occurrence_id"] is None and detached["ended_at"]
            assert detached["topic_id"] == topic["id"]
            request(a, "DELETE", path, 204)
            request(a, "DELETE", task_path, 204)
            print("PASS: owner/topic foreign keys and session preservation after schedule deletion", flush=True)
        finally:
            for client in clients:
                client.close()
            for user_id in users:
                try:
                    response = provider.delete(base+"/auth/v1/admin/users/"+user_id,
                                               headers={"apikey":secret_key,"Authorization":"Bearer "+secret_key})
                    cleaned = cleaned and response.status_code in (200,204)
                except httpx.RequestError:
                    cleaned = False
            print("Temporary verification accounts removed: " + ("yes" if cleaned else "FAILED"), flush=True)
            assert cleaned, "Temporary verification cleanup requires attention"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="Create temporary confirmed Auth users and run narrow live checks")
    parser.add_argument("--api-url", default="http://localhost:8001")
    args = parser.parse_args()
    if not args.run:
        parser.error("Explicit --run is required for live verification")
    try:
        verify(args.api_url.rstrip("/"))
    except Exception as error:
        # Do not print HTTP/SQL exception payloads, tokens, IDs, emails or settings.
        print("Planner verification failed: " + type(error).__name__, flush=True)
        if isinstance(error, AssertionError):
            print(str(error), flush=True)
        sys.exit(1)
