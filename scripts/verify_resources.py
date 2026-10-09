"""Explicit Phase 7 smoke checks using synthetic in-memory files and temporary users."""
import argparse
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


def pdf_bytes(content="Resource verification text"):
    # Small deterministic text PDF; no fixture uploads or personal source files on disk.
    stream = f"BT /F1 12 Tf 40 100 Td ({content}) Tj ET".encode("ascii")
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>",
               b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
               b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
               b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
               f"<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"\nendstream"]
    result = b"%PDF-1.4\n"
    offsets = []
    for index, obj in enumerate(objects, 1):
        offsets.append(len(result))
        result += f"{index} 0 obj\n".encode() + obj + b"\nendobj\n"
    xref = len(result)
    result += b"xref\n0 6\n0000000000 65535 f \n"
    result += b"".join(f"{offset:010d} 00000 n \n".encode() for offset in offsets)
    return result + f"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()


def check(response, status=200):
    assert response.status_code == status, f"Resource request expected {status}; received {response.status_code}"
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3001", "Resource CORS response missing"
    return response.json() if status != 204 else None


def verify(api_url):
    backend = dotenv_values(ROOT / "backend/.env")
    frontend = dotenv_values(ROOT / "frontend/.env.local")
    base, key = backend["SUPABASE_URL"].rstrip("/"), backend["SUPABASE_SECRET_KEY"]
    publishable = frontend["NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY"]
    users, clients, uploaded = [], [], []
    phase = "temporary identity setup"
    with httpx.Client(timeout=45) as provider:
        try:
            for _ in range(2):
                email, password = f"study-hub-resource-verify-{uuid4().hex}@example.com", secrets.token_urlsafe(32)
                response = provider.post(base + "/auth/v1/admin/users", headers={"apikey": key},
                                         json={"email": email, "password": password, "email_confirm": True})
                assert response.status_code in (200, 201), "Temporary user creation unavailable"
                users.append(response.json()["id"])
                login = provider.post(base + "/auth/v1/token", params={"grant_type": "password"},
                                      headers={"apikey": publishable}, json={"email": email, "password": password})
                assert login.status_code == 200, "Temporary user sign-in failed"
                clients.append(httpx.Client(base_url=api_url, timeout=60,
                    headers={"Origin": "http://localhost:3001", "Authorization": "Bearer " + login.json()["access_token"]}))
            a, b = clients
            phase = "authentication, health and preflight"
            check(a.get("/health"))
            assert check(a.get("/api/auth/me"))["id"] == users[0]
            preflight = provider.options(api_url + "/api/resources/upload", headers={"Origin": "http://localhost:3001",
                "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "authorization,content-type"})
            assert preflight.status_code == 200 and preflight.headers.get("access-control-allow-origin") == "http://localhost:3001"
            assert provider.get(api_url + "/api/resources").status_code == 401
            subjects = check(a.get("/api/subjects"))
            topic = check(a.get(f"/api/subjects/{subjects[0]['id']}/topics"))[0]
            csv = b"topic,notes\n" + b"".join(f"Topic {index},Synthetic note {index}\n".encode() for index in range(25))
            pdf = pdf_bytes()

            def upload(client, filename, content, mime, **data):
                response = client.post("/api/resources/upload", files={"file": (filename, content, mime)}, data=data)
                if response.status_code == 201:
                    uploaded.append((client, response.json()["id"]))
                return response

            phase = "PDF and CSV processing"
            resource = check(upload(a, "synthetic.pdf", pdf, "application/pdf", title="Verification PDF",
                                    subject_id=subjects[0]["id"], topic_id=topic["id"]), 201)
            assert resource["processing_status"] == "ready" and resource["page_count"] == 1
            assert "storage_path" not in resource and "user_id" not in resource
            sections = check(a.get(f"/api/resources/{resource['id']}/content"))
            assert sections["total_sections"] == 1 and sections["sections"][0]["page_number"] == 1
            assert "Resource verification text" in sections["sections"][0]["content"]
            sheet = check(upload(a, "synthetic.csv", csv, "text/csv", title="Verification CSV"), 201)
            assert sheet["row_count"] == 25 and sheet["processing_status"] == "ready"
            preview = check(a.get(f"/api/resources/{sheet['id']}/content"))
            assert preview["headers"] == ["topic", "notes"] and preview["row_count"] == 25 and len(preview["rows"]) == 20
            image = check(upload(a, "scanned.pdf", pdf_bytes(""), "application/pdf"), 201)
            assert image["processing_status"] == "failed" and image["error_message"]
            other = check(upload(b, "other.csv", b"name,value\nOther,1\n", "text/csv"), 201)
            print("PASS: text PDF pages, CSV headers/25-row count/20-row preview, and no-text PDF failure", flush=True)
            phase = "invalid files, size and associations"
            for filename, content, mime in [("renamed.pdf", b"not a PDF", "application/pdf"),
                                             ("binary.csv", b"\x00\xff\x01", "text/csv")]:
                assert upload(a, filename, content, mime).status_code in (415, 422)
            for content in [b"a,b\n1\n", b'a,b\n"unfinished,2\n']:
                check(upload(a, "malformed.csv", content, "text/csv"), 422)
            check(upload(a, "unsupported.zip", b"PK\x03\x04", "application/zip"), 415)
            check(upload(a, "large.csv", b"x\n" + b"a" * (4 * 1024 * 1024), "text/csv"), 413)
            check(upload(a, "relation.csv", b"a,b\n1,2\n", "text/csv", subject_id=subjects[1]["id"], topic_id=topic["id"]), 422)
            check(upload(a, "ownership.csv", b"a,b\n1,2\n", "text/csv", user_id=users[1]), 422)
            print("PASS: renamed/binary/malformed/unsupported/oversized files and invalid ownership/relationships rejected", flush=True)
            phase = "owner isolation and download"
            for client, foreign in [(a, other), (b, resource)]:
                for suffix in ["", "/content", "/download"]:
                    check(client.get(f"/api/resources/{foreign['id']}{suffix}"), 404)
                check(client.delete(f"/api/resources/{foreign['id']}"), 404)
                listed = check(client.get("/api/resources"))
                assert foreign["id"] not in [r["id"] for r in listed["resources"]]
            filtered = check(a.get("/api/resources", params={"subject_id": subjects[0]["id"], "resource_type": "pdf", "q": "Verification"}))
            assert [r["id"] for r in filtered["resources"]] == [resource["id"]]
            for item, content in [(resource, pdf), (sheet, csv)]:
                link = check(a.get(f"/api/resources/{item['id']}/download"))
                assert link["expires_in"] == 120 and link["url"].startswith(base + "/storage/v1/")
                downloaded = provider.get(link["url"])
                assert downloaded.status_code == 200 and downloaded.content == content
            print("PASS: owner-scoped list/detail/content/download/delete and signed original downloads", flush=True)

            phase = "database RLS and storage policies"
            with get_engine().connect() as db:
                rows = db.execute(text("SELECT id,user_id,storage_path FROM public.resources WHERE user_id IN (:a,:b)"),
                                  {"a": users[0], "b": users[1]}).mappings().all()
                db.rollback()
                own = next(row for row in rows if str(row["id"]) == resource["id"])
                for user_id in users:
                    with db.begin():
                        db.execute(text("SET LOCAL ROLE authenticated"))
                        db.execute(text("SELECT set_config('request.jwt.claims', :claims, true)"), {"claims": json.dumps({"sub": user_id, "role": "authenticated"})})
                        assert db.execute(text("SELECT count(*) FROM public.resources WHERE user_id <> :owner"), {"owner": user_id}).scalar() == 0
                        assert db.execute(text("SELECT count(*) FROM public.document_sections d JOIN public.resources r ON r.id=d.resource_id WHERE r.user_id <> :owner"), {"owner": user_id}).scalar() == 0
                        assert db.execute(text("SELECT count(*) FROM public.resources WHERE user_id=:owner"), {"owner": user_id}).scalar() > 0
                        assert not db.execute(text("SELECT has_table_privilege('authenticated','public.resources','INSERT')")).scalar()
                        assert not db.execute(text("SELECT has_table_privilege('authenticated','public.document_sections','DELETE')")).scalar()
                bucket = provider.get(base + "/storage/v1/bucket/study-resources", headers={"apikey": key})
                assert bucket.status_code == 200 and bucket.json()["public"] is False
                for client, expected in [(a, True), (b, False)]:
                    result = provider.get(base + "/storage/v1/object/authenticated/study-resources/" + own["storage_path"],
                        headers={"apikey": publishable, "Authorization": client.headers["Authorization"]})
                    assert (result.status_code == 200) == expected
                browser_write = provider.post(base + "/storage/v1/object/study-resources/" + users[0] + "/unauthorized.csv",
                    headers={"apikey": publishable, "Authorization": a.headers["Authorization"], "Content-Type": "text/csv"}, content=b"x\n1\n")
                assert browser_write.status_code not in (200, 201), "Direct browser storage write unexpectedly succeeded"
                print("PASS: metadata/sections RLS, private storage owner reads and browser mutation denial", flush=True)
            phase = "deletion"
            for client, resource_id in uploaded[:]:
                check(client.delete(f"/api/resources/{resource_id}"), 204)
                check(client.get(f"/api/resources/{resource_id}"), 404)
                uploaded.remove((client, resource_id))
            with get_engine().connect() as db:
                assert db.execute(text("SELECT count(*) FROM public.resources WHERE user_id IN (:a,:b)"), {"a": users[0], "b": users[1]}).scalar() == 0
                for row in rows:
                    assert db.execute(text("SELECT count(*) FROM storage.objects WHERE bucket_id='study-resources' AND name=:path"), {"path": row["storage_path"]}).scalar() == 0
                    assert db.execute(text("SELECT count(*) FROM public.document_sections WHERE resource_id=:id"), {"id": row["id"]}).scalar() == 0
            print("PASS: metadata, document sections and storage originals removed through authenticated deletion", flush=True)
        except Exception:
            print("Resource verification failed during " + phase + "; sensitive details withheld", flush=True)
            raise
        finally:
            cleaned = True
            for client, resource_id in uploaded:
                try:
                    cleaned = client.delete(f"/api/resources/{resource_id}").status_code == 204 and cleaned
                except Exception:
                    cleaned = False
            # Keep identities/metadata for retry if an object cleanup failed; cascading
            # profiles away first would lose the object's trustworthy cleanup locator.
            for user_id in users if cleaned else []:
                try:
                    cleaned = provider.delete(base + "/auth/v1/admin/users/" + user_id, headers={"apikey": key}).status_code in (200, 204) and cleaned
                except Exception:
                    cleaned = False
            for client in clients:
                client.close()
            print("Synthetic verification data/account cleanup: " + ("PASS" if cleaned else "FAILED"), flush=True)
            assert cleaned, "Synthetic cleanup requires attention"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--api-url", default="http://localhost:8001")
    args = parser.parse_args()
    if not args.run:
        parser.error("Explicit --run is required to create synthetic verification data")
    try:
        verify(args.api_url.rstrip("/"))
    except Exception:
        sys.exit(1)
