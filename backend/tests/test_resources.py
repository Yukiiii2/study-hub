"""Focused resource parsing, auth, ownership, storage and failure-order checks."""
import importlib.util
import unittest
from contextlib import contextmanager
from datetime import datetime, timezone
from io import BytesIO
from unittest.mock import patch
from uuid import UUID

import httpx
from sqlalchemy.exc import SQLAlchemyError

from app.main import app
from app.core.auth import get_current_user
from app.schemas.auth import AuthenticatedUser

USER = UUID("00000000-0000-4000-8000-000000000001")
RESOURCE = UUID("00000000-0000-4000-8000-000000000301")
NOW = datetime(2026, 10, 7, tzinfo=timezone.utc)


def metadata(**changes):
    return dict(id=RESOURCE, subject_id=None, topic_id=None, subject_code=None, topic_title=None,
                title="Study notes", original_filename="notes.csv", mime_type="text/csv", file_size_bytes=8,
                resource_type="csv", processing_status="ready", page_count=None, row_count=1,
                error_message=None, created_at=NOW, updated_at=NOW, **changes)


@contextmanager
def transaction():
    yield object()


class ParserChecks(unittest.TestCase):
    def test_csv_parser_available(self):
        self.assertIsNotNone(importlib.util.find_spec("app.parsers.csv_parser"), "CSV parser is not implemented")

    def test_csv_bom_multiline_full_count_and_bounded_preview(self):
        from app.parsers.csv_parser import parse_csv
        data = '\ufeffname,note\n"Ada","line one\nline two"\n' + ''.join(f'{i},ok\n' for i in range(25))
        result = parse_csv(data.encode())
        self.assertEqual(result.headers, ["name", "note"])
        self.assertEqual(result.row_count, 26)
        self.assertEqual(len(result.rows), 20)
        self.assertEqual(result.rows[0], ["Ada", "line one\nline two"])

    def test_csv_rejects_decode_binary_header_shape_and_bad_quoting(self):
        from app.parsers.csv_parser import parse_csv
        from app.services.resource_errors import ResourceError
        for data in (b"\xff\xfea,b", b"a,b\n\0,x", b"a,a\nx,y", b",b\nx,y", b"a,b\nx", b'a,b\n"unterminated,x', b'a,b\n"x"junk,y', b'a,b\nx"y,z\n', b"", b"a,b\n"):
            with self.subTest(data=data), self.assertRaises(ResourceError) as caught:
                parse_csv(data)
            self.assertEqual(caught.exception.status_code, 422)
        # Invalid rows after the preview still invalidate the entire file.
        with self.assertRaises(ResourceError):
            parse_csv(b"a,b\n" + b"x,y\n" * 21 + b"wrong\n")

    def test_pdf_text_and_blank_pages_preserve_page_numbers(self):
        from pypdf import PdfWriter
        from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject
        from app.parsers.pdf_parser import parse_pdf
        writer = PdfWriter()
        font = DictionaryObject({NameObject("/Type"): NameObject("/Font"), NameObject("/Subtype"): NameObject("/Type1"), NameObject("/BaseFont"): NameObject("/Helvetica")})
        page = writer.add_blank_page(width=300, height=300)
        page[NameObject("/Resources")] = DictionaryObject({NameObject("/Font"): DictionaryObject({NameObject("/F1"): writer._add_object(font)})})
        stream = DecodedStreamObject()
        stream.set_data(b"BT /F1 12 Tf 20 200 Td (CPA notes) Tj ET")
        page[NameObject("/Contents")] = writer._add_object(stream)
        writer.add_blank_page(width=300, height=300)
        output = BytesIO()
        writer.write(output)
        result = parse_pdf(output.getvalue())
        self.assertEqual(result.processing_status, "ready")
        self.assertEqual(result.page_count, 2)
        self.assertEqual([s["page_number"] for s in result.sections], [1, 2])
        self.assertIn("CPA notes", result.sections[0]["content"])

    def test_pdf_no_text_and_invalid_pdf_fail_safely(self):
        from pypdf import PdfWriter
        from app.parsers.pdf_parser import parse_pdf
        writer = PdfWriter()
        writer.add_blank_page(width=300, height=300)
        output = BytesIO()
        writer.write(output)
        blank = parse_pdf(output.getvalue())
        self.assertEqual(blank.processing_status, "failed")
        self.assertIn("text", blank.error_message.lower())
        broken = parse_pdf(b"%PDF-1.7\nnot valid private bytes")
        self.assertEqual(broken.processing_status, "failed")
        self.assertNotIn("private bytes", broken.error_message)

    def test_csv_preview_response_is_bounded(self):
        from app.parsers.csv_parser import parse_csv
        from app.services.resource_errors import ResourceError
        data = b"a,b\n" + (b"x" * 9000 + b"," + b"y" * 9000 + b"\n") * 20
        with self.assertRaises(ResourceError):
            parse_csv(data)

    def test_empty_pdf_retains_valid_nullable_page_count(self):
        from pypdf import PdfWriter
        from app.parsers.pdf_parser import parse_pdf
        writer = PdfWriter()
        output = BytesIO()
        writer.write(output)
        result = parse_pdf(output.getvalue())
        self.assertEqual(result.processing_status, "failed")
        self.assertIsNone(result.page_count)

    def test_pdf_form_content_and_invocations_are_bounded_without_partial_ready(self):
        from pypdf import PdfWriter
        from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject, ArrayObject, NumberObject
        from app.parsers import pdf_parser
        def document(repetitions, indirect_resources=False):
            writer = PdfWriter()
            page = writer.add_blank_page(width=300, height=300)
            font = DictionaryObject({NameObject("/Type"): NameObject("/Font"), NameObject("/Subtype"): NameObject("/Type1"), NameObject("/BaseFont"): NameObject("/Helvetica")})
            form = DecodedStreamObject()
            form.set_data(b"BT /F1 12 Tf 20 200 Td (Form source text) Tj ET")
            form[NameObject("/Type")] = NameObject("/XObject")
            form[NameObject("/Subtype")] = NameObject("/Form")
            form[NameObject("/BBox")] = ArrayObject([NumberObject(0), NumberObject(0), NumberObject(300), NumberObject(300)])
            form_resources = DictionaryObject({NameObject("/Font"): DictionaryObject({NameObject("/F1"): writer._add_object(font)})})
            form[NameObject("/Resources")] = writer._add_object(form_resources) if indirect_resources else form_resources
            forms = DictionaryObject({NameObject("/Form1"): writer._add_object(form)})
            page_resources = DictionaryObject({NameObject("/XObject"): writer._add_object(forms) if indirect_resources else forms})
            page[NameObject("/Resources")] = writer._add_object(page_resources) if indirect_resources else page_resources
            contents = DecodedStreamObject()
            contents.set_data(b"/Form1 Do\n" * repetitions)
            page[NameObject("/Contents")] = writer._add_object(contents)
            output = BytesIO()
            writer.write(output)
            return output.getvalue()
        self.assertEqual(pdf_parser.parse_pdf(document(1)).processing_status, "ready")
        self.assertEqual(pdf_parser.parse_pdf(document(1, indirect_resources=True)).processing_status, "ready")
        with patch.object(pdf_parser, "MAX_TOTAL_STREAM_BYTES", 100):
            self.assertEqual(pdf_parser.parse_pdf(document(2)).processing_status, "failed")
        self.assertEqual(pdf_parser.parse_pdf(document(201)).processing_status, "failed")


class ResourceApiChecks(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")

    async def asyncTearDown(self):
        app.dependency_overrides.clear()
        await self.client.aclose()

    def signed_in(self):
        app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id=USER, email=None)

    async def test_every_resource_route_requires_auth(self):
        for method, path in (("GET", "/api/resources"), ("POST", "/api/resources/upload"), ("GET", f"/api/resources/{RESOURCE}"), ("DELETE", f"/api/resources/{RESOURCE}"), ("GET", f"/api/resources/{RESOURCE}/download"), ("GET", f"/api/resources/{RESOURCE}/content")):
            response = await self.client.request(method, path)
            self.assertEqual(response.status_code, 401, path)

    async def test_upload_rejects_ownership_extras_and_duplicate_fields(self):
        self.signed_in()
        for form in ({"user_id": str(USER)}, {"storage_path": "private"}, {"title": ["a", "b"]}):
            response = await self.client.post("/api/resources/upload", data=form, files={"file": ("notes.csv", b"a,b\nx,y\n", "text/csv")})
            self.assertEqual(response.status_code, 422)

    async def test_upload_rejects_renamed_binary_mime_and_file_size(self):
        self.signed_in()
        for name, content, mime, status in (("notes.csv", b"PK\x03\x04binary", "text/csv", 422), ("notes.pdf", b"a,b\nx,y\n", "application/pdf", 415), ("notes.csv", b"a,b\nx,y", "application/pdf", 415), ("notes.csv", b"x" * (4194304 + 1), "text/csv", 413)):
            response = await self.client.post("/api/resources/upload", files={"file": (name, content, mime)})
            self.assertEqual(response.status_code, status)

    async def test_request_body_is_bounded_before_multipart_parser(self):
        self.signed_in()
        async def body():
            for _ in range(70):
                yield b"x" * 65536
        response = await self.client.post("/api/resources/upload", content=body(), headers={"Content-Type": "multipart/form-data; boundary=x"})
        self.assertEqual(response.status_code, 413)

    async def test_malformed_multipart_is_a_safe_input_error(self):
        self.signed_in()
        response = await self.client.post("/api/resources/upload", content=b"wrong private form bytes", headers={"Content-Type": "multipart/form-data; boundary=x"})
        self.assertEqual(response.status_code, 422)
        self.assertNotIn("private", response.text)

    async def test_resource_queries_preserve_contract_and_safe_errors(self):
        self.signed_in()
        with patch("app.services.resources.list_resources", return_value={"resources": [metadata()], "total": 1}):
            response = await self.client.get("/api/resources?limit=100&offset=3&q=notes")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["resources"][0]["title"], "Study notes")
        self.assertNotIn("user_id", response.json()["resources"][0])
        self.assertEqual((await self.client.get("/api/resources?limit=101")).status_code, 422)
        with patch("app.services.resources.get_resource", side_effect=SQLAlchemyError("private connection")):
            response = await self.client.get(f"/api/resources/{RESOURCE}")
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("private connection", response.text)


class ResourceFailureChecks(unittest.TestCase):
    def test_pdf_processing_follows_stored_original_and_metadata(self):
        from app.services import resources
        from app.schemas.resources import UploadMetadata
        from app.parsers.pdf_parser import PdfContent
        operations = []
        class Storage:
            def upload(self, *args): operations.append("storage")
            def delete(self, *args): operations.append("cleanup")
        def insert(connection, owner, data, sections):
            operations.append("metadata")
            self.assertEqual(data["processing_status"], "uploaded")
            self.assertEqual(sections, [])
            return {**metadata(), **data}
        def parse(data):
            operations.append("parse")
            return PdfContent("failed", error_message="No selectable text was found. OCR is not supported.")
        def finish(connection, owner, resource_id, values, sections):
            operations.append("finish")
            return {**metadata(), "resource_type": "pdf", "mime_type": "application/pdf", **values, "row_count": None}
        with patch.object(resources.repo, "transaction", transaction), patch.object(resources.repo, "valid_associations", return_value=True), patch.object(resources.repo, "insert_resource", side_effect=insert), patch.object(resources.repo, "mark_processing", side_effect=lambda *args: operations.append("processing")), patch.object(resources.repo, "finish_processing", side_effect=finish), patch.object(resources, "parse_pdf", side_effect=parse), self.assertLogs(resources.logger, level="WARNING") as logs:
            result = resources.upload_resource(USER, "notes.pdf", "application/pdf", b"%PDF-1.4", UploadMetadata(), storage=Storage())
        self.assertEqual(operations, ["storage", "metadata", "processing", "parse", "finish"])
        self.assertEqual(result.processing_status, "failed")
        self.assertNotIn("No selectable", " ".join(logs.output))

    def test_original_filename_is_preserved_and_object_name_is_sanitized(self):
        from app.services import resources
        from app.schemas.resources import UploadMetadata
        recorded = {}
        class Storage:
            def upload(self, path, data, mime):
                recorded["path"] = path
        def insert(connection, user_id, data, sections):
            recorded.update(data)
            return {**metadata(), **data, "subject_code": None, "topic_title": None, "created_at": NOW, "updated_at": NOW}
        with patch.object(resources.repo, "transaction", transaction), patch.object(resources.repo, "valid_associations", return_value=True), patch.object(resources.repo, "insert_resource", side_effect=insert), patch.object(resources.repo, "mark_processing"), patch.object(resources.repo, "finish_processing", side_effect=lambda c, u, i, v, s: insert(c, u, v, s)):
            result = resources.upload_resource(USER, "Study & notes.csv", "text/csv", b"a,b\nx,y\n", UploadMetadata(), storage=Storage())
        self.assertEqual(result.original_filename, "Study & notes.csv")
        self.assertNotIn("&", recorded["path"])

    def test_upload_database_failure_removes_new_object(self):
        from app.services import resources
        from app.schemas.resources import UploadMetadata
        operations = []
        class Storage:
            def upload(self, path, data, mime):
                operations.append("uploaded")
            def delete(self, path):
                operations.append("compensated")
        with patch.object(resources.repo, "transaction", transaction), patch.object(resources.repo, "valid_associations", return_value=True), patch.object(resources.repo, "insert_resource", side_effect=SQLAlchemyError("private")):
            with self.assertRaises(SQLAlchemyError):
                resources.upload_resource(USER, "notes.csv", "text/csv", b"a,b\nx,y\n", UploadMetadata(), storage=Storage())
        self.assertEqual(operations, ["uploaded", "compensated"])

    def test_uncertain_storage_upload_response_also_attempts_cleanup(self):
        from app.services import resources
        from app.schemas.resources import UploadMetadata
        from app.services.resource_errors import ResourceError
        operations = []
        class Storage:
            def upload(self, *args):
                operations.append("provider may have stored file")
                raise ResourceError(503, "File storage is unavailable. Try again.")
            def delete(self, path): operations.append("compensated")
        with patch.object(resources.repo, "transaction", transaction), patch.object(resources.repo, "valid_associations", return_value=True):
            with self.assertRaises(ResourceError):
                resources.upload_resource(USER, "notes.csv", "text/csv", b"a,b\nx,y\n", UploadMetadata(), storage=Storage())
        self.assertEqual(operations, ["provider may have stored file", "compensated"])

    def test_delete_storage_failure_preserves_metadata(self):
        from app.services import resources
        from app.services.resource_errors import ResourceError
        operations = []
        class Storage:
            def delete(self, path):
                operations.append("storage failed")
                raise ResourceError(503, "Storage is unavailable.")
        record = {**metadata(), "storage_path": f"{USER}/{RESOURCE}/notes.csv", "storage_bucket": "study-resources"}
        with patch.object(resources.repo, "transaction", transaction), patch.object(resources.repo, "get_resource", return_value=record), patch.object(resources.repo, "delete_resource", side_effect=lambda *args: operations.append("metadata deleted")):
            with self.assertRaises(ResourceError):
                resources.delete_resource(USER, RESOURCE, storage=Storage())
        self.assertEqual(operations, ["storage failed"])

    def test_missing_owner_record_never_contacts_storage(self):
        from app.services import resources
        from app.services.resource_errors import ResourceError
        class Storage:
            def delete(self, path):
                raise AssertionError("Other-user storage contacted")
        with patch.object(resources.repo, "transaction", transaction), patch.object(resources.repo, "get_resource", return_value=None):
            with self.assertRaises(ResourceError) as caught:
                resources.delete_resource(USER, RESOURCE, storage=Storage())
        self.assertEqual(caught.exception.status_code, 404)


class StorageChecks(unittest.TestCase):
    def test_setup_creates_bucket_for_typed_missing_error_and_verifies_limits(self):
        from app.services.resource_storage import ResourceStorage
        from app.core.config import Settings
        settings = Settings(_env_file=None, supabase_url="https://example.supabase.co", supabase_secret_key="sb_secret_test")
        requests = []
        def handler(request):
            requests.append(request)
            if len(requests) == 1:
                return httpx.Response(400, json={"statusCode": "404", "error": "not_found"})
            if request.method == "POST":
                return httpx.Response(200, json={"name": "study-resources"})
            return httpx.Response(200, json={"id": "study-resources", "public": False, "file_size_limit": 4194304, "allowed_mime_types": ["application/pdf", "text/csv"]})
        with httpx.Client(transport=httpx.MockTransport(handler)) as client:
            result = ResourceStorage(settings=settings, client=client).ensure_bucket()
        self.assertFalse(result["public"])
        self.assertEqual([request.method for request in requests], ["GET", "POST", "GET"])

    def test_setup_rejects_public_or_unrestricted_bucket(self):
        from app.services.resource_storage import ResourceStorage
        from app.services.resource_errors import ResourceError
        from app.core.config import Settings
        settings = Settings(_env_file=None, supabase_url="https://example.supabase.co", supabase_secret_key="sb_secret_test")
        for config in ({"id": "study-resources", "public": True}, {"id": "study-resources", "public": False}):
            with self.subTest(config=config), httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(200, json=config))) as client:
                with self.assertRaises(ResourceError):
                    ResourceStorage(settings=settings, client=client).ensure_bucket()

    def test_secret_key_is_only_apikey_and_signed_url_is_transient(self):
        from app.services.resource_storage import ResourceStorage
        from app.core.config import Settings
        settings = Settings(_env_file=None, supabase_url="https://example.supabase.co", supabase_secret_key="sb_secret_test")
        requests = []
        def handler(request):
            requests.append(request)
            return httpx.Response(200, json={"signedURL": "/object/sign/study-resources/own/notes.csv?token=temporary"})
        with httpx.Client(transport=httpx.MockTransport(handler)) as client:
            url = ResourceStorage(settings=settings, client=client).sign("own/notes.csv", download=True)
        self.assertTrue(url.startswith("https://example.supabase.co/storage/v1/object/sign/"))
        self.assertEqual(requests[0].headers["apikey"], "sb_secret_test")
        self.assertNotIn("authorization", requests[0].headers)

    def test_delete_missing_object_is_retry_safe_but_outage_fails(self):
        from app.services.resource_storage import ResourceStorage
        from app.services.resource_errors import ResourceError
        from app.core.config import Settings
        settings = Settings(_env_file=None, supabase_url="https://example.supabase.co", supabase_secret_key="sb_secret_test")
        with httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(404, json={"statusCode": "404", "error": "not_found"}))) as client:
            ResourceStorage(settings=settings, client=client).delete("own/notes.csv")
        with httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(500, text="private provider error"))) as client:
            with self.assertRaises(ResourceError) as caught:
                ResourceStorage(settings=settings, client=client).delete("own/notes.csv")
        self.assertNotIn("private", caught.exception.detail)


if __name__ == "__main__":
    unittest.main()
