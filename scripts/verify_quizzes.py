"""Explicit Phase 8 lifecycle checks; only synthetic temporary identities/data."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
from io import StringIO
import json
from pathlib import Path
import secrets
import sys
from uuid import uuid4

import httpx
from dotenv import dotenv_values
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.db.connection import get_engine
from verify_resources import pdf_bytes


def check(response, status=200):
    assert response.status_code == status, f"Expected {status}; received {response.status_code}"
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3001"
    return response.json() if status != 204 else None


def protected(attempt):
    hidden = {"correct_keys", "is_correct", "explanation", "snapshot", "question_snapshot", "user_id"}
    def walk(value):
        if isinstance(value, dict):
            assert not hidden.intersection(value), "Answer key leaked before submission"
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)
    walk(attempt)


def csv_bytes(rows):
    out = StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=["subject", "topic", "question_type", "question", "option_a", "option_b", "option_c", "option_d", "correct_answer", "explanation"])
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode("utf-8")


def verify(api_url):
    backend = dotenv_values(ROOT / "backend/.env")
    frontend = dotenv_values(ROOT / "frontend/.env.local")
    base = backend["SUPABASE_URL"].rstrip("/")
    key, public = backend["SUPABASE_SECRET_KEY"], frontend["NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY"]
    users, clients, resources = [], [], []
    phase = "temporary authentication"
    with httpx.Client(timeout=45) as provider:
        try:
            for _ in range(2):
                email = f"study-hub-quiz-verify-{uuid4().hex}@example.com"
                password = secrets.token_urlsafe(32)
                made = provider.post(base + "/auth/v1/admin/users", headers={"apikey": key}, json={"email": email, "password": password, "email_confirm": True})
                assert made.status_code in (200, 201)
                users.append(made.json()["id"])
                login = provider.post(base + "/auth/v1/token", params={"grant_type": "password"}, headers={"apikey": public}, json={"email": email, "password": password})
                assert login.status_code == 200
                clients.append(httpx.Client(base_url=api_url, timeout=60, headers={"Origin": "http://localhost:3001", "Authorization": "Bearer " + login.json()["access_token"]}))
            a, b = clients
            phase = "questions and source ownership"
            check(a.get("/health"))
            assert check(a.get("/api/auth/me"))["id"] == users[0]
            assert provider.get(api_url + "/api/quizzes").status_code == 401
            subjects = check(a.get("/api/subjects"))
            topic = check(a.get(f"/api/subjects/{subjects[0]['id']}/topics"))[0]
            resource = check(a.post("/api/resources/upload", files={"file": ("quiz-verification.pdf", pdf_bytes(), "application/pdf")}), 201)
            resources.append((a, resource["id"]))
            common = {"subject_id": subjects[0]["id"], "topic_id": topic["id"], "resource_id": resource["id"], "source_page": 1,
                      "explanation": "Synthetic verification explanation"}
            single = {**common, "question_type": "single_select", "prompt": "Synthetic single-select verification",
                      "options": [{"key": "A", "text": "First"}, {"key": "B", "text": "Second"}], "correct_keys": ["A"]}
            multi = {**common, "question_type": "multi_select", "prompt": "Synthetic multi-select verification",
                     "options": [{"key": "A", "text": "First"}, {"key": "B", "text": "Second"}, {"key": "C", "text": "Third"}], "correct_keys": ["A", "C"]}
            tf = {**common, "question_type": "true_false", "prompt": "Synthetic true-false verification",
                  "options": [{"key": "TRUE", "text": "True"}, {"key": "FALSE", "text": "False"}], "correct_keys": ["TRUE"]}
            questions = [check(a.post("/api/questions", json=value), 201) for value in (single, multi, tf)]
            assert check(a.get("/api/questions"))["total"] == 3
            check(b.post("/api/questions", json=single), 422)
            check(a.post("/api/questions", json={**single, "prompt": "Wrong relationship", "subject_id": subjects[1]["id"]}), 422)
            check(a.post("/api/questions", json={**single, "prompt": "Wrong page", "source_page": 2}), 422)
            check(a.post("/api/questions", json={**single, "prompt": "Wrong ownership", "user_id": users[1]}), 422)
            check(a.post("/api/questions", json={**single, "prompt": "Wrong option", "correct_keys": ["X"]}), 422)
            check(a.post("/api/questions", json=single), 409)
            print("PASS: manual question formats, answer validation, source/page/topic ownership", flush=True)

            phase = "ordered quizzes and answer protection"
            quiz_input = {"title": "Synthetic quiz verification", "description": "Temporary verification only", "subject_id": subjects[0]["id"], "topic_id": topic["id"], "question_ids": [q["id"] for q in questions]}
            quiz = check(a.post("/api/quizzes", json=quiz_input), 201)
            protected(quiz)
            assert [q["id"] for q in quiz["questions"]] == quiz_input["question_ids"]
            check(b.post("/api/quizzes", json=quiz_input), 404)
            for route in ["/api/questions/" + questions[0]["id"], "/api/quizzes/" + quiz["id"]]:
                check(b.get(route), 404)
                check(b.patch(route, json={"is_archived": True}), 404)
            attempt = check(a.post(f"/api/quizzes/{quiz['id']}/attempts"))
            same = check(a.post(f"/api/quizzes/{quiz['id']}/attempts"))
            assert same["id"] == attempt["id"]
            protected(attempt)
            route = "/api/quiz-attempts/" + attempt["id"]
            check(a.get(route + "/results"), 409)
            check(a.post(route + "/answers", json={"question_id": questions[0]["id"], "selected_keys": ["X"]}), 422)
            check(a.post(route + "/answers", json={"question_id": questions[0]["id"], "selected_keys": ["A", "B"]}), 422)
            check(a.post(route + "/answers", json={"question_id": questions[0]["id"], "selected_keys": ["A"], "is_correct": True}), 422)
            for question, keys in [(questions[0], ["A"]), (questions[1], ["A"])]:
                saved = check(a.post(route + "/answers", json={"question_id": question["id"], "selected_keys": keys}))
                protected(saved)
            loaded = check(a.get(route))
            assert loaded["questions"][0]["selected_keys"] == ["A"] and loaded["questions"][1]["selected_keys"] == ["A"]
            protected(loaded)
            check(a.patch("/api/questions/" + questions[0]["id"], json={**single, "correct_keys": ["B"], "explanation": "Edited after start"}))
            check(a.patch("/api/quizzes/" + quiz["id"], json={**quiz_input, "question_ids": list(reversed(quiz_input["question_ids"]))}))
            frozen = check(a.get(route))
            assert [q["id"] for q in frozen["questions"]] == quiz_input["question_ids"]
            check(b.get(route), 404)
            check(b.post(route + "/answers", json={"question_id": questions[0]["id"], "selected_keys": ["A"]}), 404)
            check(b.post(route + "/complete"), 404)
            print("PASS: ordering, active resume, frozen snapshot, persisted reload and protected pre-submit DTOs", flush=True)

            phase = "atomic grading and history"
            done = check(a.post(route + "/complete"))
            assert done["status"] == "completed" and done["score_value"] == 1 and done["total_questions"] == 3 and done["score_percent"] == 33.33
            assert done["questions"][0]["correct_keys"] == ["A"]
            assert done["questions"][0]["explanation"] == single["explanation"]
            assert [q["is_correct"] for q in done["questions"]] == [True, False, False]
            assert check(a.post(route + "/complete")) == done
            assert check(a.get(route + "/results")) == done
            check(a.post(route + "/answers", json={"question_id": questions[0]["id"], "selected_keys": ["B"]}), 409)
            assert check(a.get("/api/quiz-attempts", params={"quiz_id": quiz["id"]}))["total"] == 1
            assert check(b.get("/api/quiz-attempts"))["total"] == 0
            print("PASS: snapshot server grading, exact-set multi-select, unanswered zero, immutable/idempotent results/history", flush=True)

            phase = "concurrent answer and submission serialization"
            second = check(a.post(f"/api/quizzes/{quiz['id']}/attempts"))
            second_route = "/api/quiz-attempts/" + second["id"]
            protected(second)
            for question_id, keys in [(questions[0]["id"], ["B"]), (questions[1]["id"], ["C", "A"]), (questions[2]["id"], ["TRUE"])]:
                check(a.post(second_route + "/answers", json={"question_id": question_id, "selected_keys": keys}))
            with ThreadPoolExecutor(max_workers=2) as pool:
                completions = list(pool.map(lambda _: check(a.post(second_route + "/complete")), range(2)))
            assert completions[0] == completions[1] and completions[0]["score_value"] == 3 and completions[0]["score_percent"] == 100
            third = check(a.post(f"/api/quizzes/{quiz['id']}/attempts"))
            third_route = "/api/quiz-attempts/" + third["id"]
            with ThreadPoolExecutor(max_workers=2) as pool:
                saving = pool.submit(a.post, third_route + "/answers", json={"question_id": questions[0]["id"], "selected_keys": ["B"]})
                submitting = pool.submit(a.post, third_route + "/complete")
                save_response, sealed = saving.result(), check(submitting.result())
            assert save_response.status_code in (200, 409)
            assert sealed["score_value"] == (1 if save_response.status_code == 200 else 0)
            assert check(a.get(third_route + "/results")) == sealed
            print("PASS: all three formats grade correctly, concurrent submit is idempotent, save/submit race is serialized", flush=True)

            phase = "CSV dry run, confirmation and idempotency"
            source = csv_bytes([{ "subject": "MS", "question_type": "single_select", "question": "Synthetic CSV verification", "option_a": "Alpha", "option_b": "Beta", "correct_answer": "A", "explanation": "Synthetic CSV explanation"}])
            def preview(client, data):
                return client.post("/api/imports/questions/preview", files={"file": ("synthetic-questions.csv", data, "text/csv")})
            report = check(preview(a, source))
            assert report["proposed_inserts"] == 1 and not report["errors"] and report["preview_token"]
            commit_data = {"preview_token": report["preview_token"]}
            check(b.post("/api/imports/questions/commit", files={"file": ("synthetic-questions.csv", source, "text/csv")}, data=commit_data), 422)
            altered = source.replace(b"Alpha", b"Gamma")
            check(a.post("/api/imports/questions/commit", files={"file": ("synthetic-questions.csv", altered, "text/csv")}, data=commit_data), 422)
            assert check(a.get("/api/questions"))["total"] == 3
            imported = check(a.post("/api/imports/questions/commit", files={"file": ("synthetic-questions.csv", source, "text/csv")}, data=commit_data))
            assert imported["inserted"] == 1
            repeated = check(preview(a, source))
            assert repeated["proposed_inserts"] == 0 and repeated["unchanged"] == 1
            rerun = check(a.post("/api/imports/questions/commit", files={"file": ("synthetic-questions.csv", source, "text/csv")}, data={"preview_token": repeated["preview_token"]}))
            assert rerun["inserted"] == 0 and rerun["unchanged"] == 1
            assert check(preview(a, altered))["errors"]
            invalid = csv_bytes([{ "subject": "UNKNOWN", "question": "Invalid mapping", "option_a": "A", "option_b": "B", "correct_answer": "A"}])
            assert check(preview(a, invalid))["errors"]
            malformed = preview(a, b'a,b\n"unfinished\n')
            assert malformed.status_code == 422 or (malformed.status_code == 200 and malformed.json()["errors"])
            assert preview(a, b"a\n" + b"x" * 1_048_576).status_code == 413
            print("PASS: validated CSV dry run, bound confirmation, MS mapping, conflict rejection and zero-insert rerun", flush=True)

            phase = "RLS and private grading-column grants"
            with get_engine().connect() as db:
                for user_id in users:
                    with db.begin():
                        db.execute(text("SET LOCAL ROLE authenticated"))
                        db.execute(text("SELECT set_config('request.jwt.claims',:claims,true)"), {"claims": json.dumps({"sub": user_id, "role": "authenticated"})})
                        for table in ("questions", "quizzes", "quiz_questions"):
                            assert db.execute(text(f"SELECT count(*) FROM public.{table} WHERE user_id <> :owner"), {"owner": user_id}).scalar() == 0
                            assert not db.execute(text(f"SELECT has_table_privilege('authenticated','public.{table}','INSERT')")).scalar()
                        assert not db.execute(text("SELECT has_column_privilege('authenticated','public.quiz_attempts','snapshot','SELECT')")).scalar()
                        assert not db.execute(text("SELECT has_table_privilege('authenticated','public.quiz_answers','SELECT')")).scalar()
                        assert not db.execute(text("SELECT has_column_privilege('authenticated','public.question_options','is_correct','SELECT')")).scalar()
            check(a.patch("/api/questions/" + questions[0]["id"], json={"is_archived": True}))
            check(a.patch("/api/quizzes/" + quiz["id"], json={"is_archived": True}))
            assert check(a.get("/api/quizzes"))["total"] == 0
            assert check(a.get(route + "/results"))["score_value"] == 1
            print("PASS: owner RLS, restricted key/snapshot grants, archive preserving attempts", flush=True)

            phase = "maximum batch import and ordered quiz snapshot"
            bulk_source = csv_bytes([{"subject": "MS", "question": f"Synthetic batch question {index}", "option_a": "Alpha", "option_b": "Beta", "correct_answer": "A"} for index in range(500)])
            bulk_report = check(preview(a, bulk_source))
            assert bulk_report["proposed_inserts"] == 500 and not bulk_report["errors"]
            bulk_result = check(a.post("/api/imports/questions/commit", files={"file": ("synthetic-batch.csv", bulk_source, "text/csv")}, data={"preview_token": bulk_report["preview_token"]}))
            assert bulk_result["inserted"] == 500
            bulk_repeat = check(preview(a, bulk_source))
            assert bulk_repeat["proposed_inserts"] == 0 and bulk_repeat["unchanged"] == 500
            bank = check(a.get("/api/questions", params={"q": "Synthetic batch question", "limit": 100}))
            assert bank["total"] == 500 and len(bank["questions"]) == 100
            order = [item["id"] for item in reversed(bank["questions"])]
            large_quiz = check(a.post("/api/quizzes", json={"title": "Synthetic maximum quiz", "question_ids": order}), 201)
            protected(large_quiz)
            assert [item["id"] for item in large_quiz["questions"]] == order
            maximum = check(a.post(f"/api/quizzes/{large_quiz['id']}/attempts"))
            protected(maximum)
            assert maximum["total_questions"] == 100 and [item["id"] for item in maximum["questions"]] == order
            maximum_route = "/api/quiz-attempts/" + maximum["id"]
            check(a.post(maximum_route + "/answers", json={"question_id": order[0], "selected_keys": ["A"]}))
            maximum_result = check(a.post(maximum_route + "/complete"))
            assert maximum_result["score_value"] == 1 and maximum_result["score_percent"] == 1
            print("PASS: 500-row transactional import/rerun, 100-row bank and 100-question ordered snapshot/grading", flush=True)
        except Exception:
            print("Quiz verification failed during " + phase + "; sensitive details withheld", flush=True)
            raise
        finally:
            cleaned = True
            for client, resource_id in resources:
                try:
                    cleaned = client.delete(f"/api/resources/{resource_id}").status_code == 204 and cleaned
                except Exception:
                    cleaned = False
            # Cascade only verified temporary identities created by this invocation.
            for user_id in users if cleaned else []:
                try:
                    cleaned = provider.delete(base + "/auth/v1/admin/users/" + user_id, headers={"apikey": key}).status_code in (200, 204) and cleaned
                except Exception:
                    cleaned = False
            for client in clients:
                client.close()
            if cleaned and users:
                try:
                    with get_engine().connect() as db:
                        assert db.execute(text("SELECT count(*) FROM auth.users WHERE id = ANY(CAST(:owners AS uuid[]))"), {"owners": users}).scalar() == 0
                        for table in ("questions", "question_options", "quizzes", "quiz_questions", "quiz_attempts", "quiz_answers", "resources", "document_sections"):
                            assert db.execute(text(f"SELECT count(*) FROM public.{table} WHERE user_id = ANY(CAST(:owners AS uuid[]))"), {"owners": users}).scalar() == 0
                except Exception:
                    cleaned = False
            print("Synthetic quiz/resource/account cleanup: " + ("PASS" if cleaned else "FAILED"), flush=True)
            assert cleaned


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--api-url", default="http://localhost:8001")
    args = parser.parse_args()
    if not args.run:
        parser.error("Explicit --run is required to create temporary synthetic data")
    try:
        verify(args.api_url.rstrip("/"))
    except Exception:
        sys.exit(1)
