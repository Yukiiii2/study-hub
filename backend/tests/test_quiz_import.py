"""Focused CSV parsing, preview identity and signed confirmation checks."""
import csv
from io import StringIO
import unittest
from contextlib import contextmanager
from unittest.mock import patch
from uuid import UUID

USER = UUID("11111111-1111-1111-1111-111111111111")
SUBJECT = UUID("22222222-2222-2222-2222-222222222222")
TOPIC = UUID("33333333-3333-3333-3333-333333333333")


@contextmanager
def transaction():
    yield object()


def csv_bytes(rows, headers=None):
    headers = headers or ["question", "option_a", "option_b", "correct_answer"]
    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


class QuizCsvParserChecks(unittest.TestCase):
    def test_bom_multiline_comma_csv_and_literal_values(self):
        from app.parsers.quiz_csv_parser import parse_quiz_csv
        parsed = parse_quiz_csv(b"\xef\xbb\xbf" + csv_bytes([{"question": "Line one\nLine two, quoted", "option_a": "1", "option_b": "2", "correct_answer": "A"}]))
        self.assertEqual(parsed.row_count, 1)
        self.assertEqual(parsed.rows[0][0], 2)
        self.assertEqual(parsed.rows[0][1]["question"], "Line one\nLine two, quoted")
        self.assertEqual(parsed.errors, [])

    def test_csv_rejects_invalid_headers_encoding_size_and_row_limit(self):
        from app.parsers.quiz_csv_parser import parse_quiz_csv, QuizImportError
        for data in (b"question,question,correct_answer\nx,x,A\n", b"question,correct_answer,owner\nx,A,u\n", b"question\nx\n", b"question;correct_answer\nx;A\n", b"question,correct_answer\n\xff,A\n"):
            with self.subTest(data=data):
                self.assertTrue(parse_quiz_csv(data).errors)
        with self.assertRaises(QuizImportError) as raised:
            parse_quiz_csv(b"x" * (1048576 + 1))
        self.assertEqual(raised.exception.status_code, 413)
        self.assertTrue(parse_quiz_csv(b"question,correct_answer\n" + b"x,A\n" * 501).errors)

    def test_malformed_quoting_and_width_are_reported(self):
        from app.parsers.quiz_csv_parser import parse_quiz_csv
        for data in (b'question,correct_answer\nwrong"quote,A\n', b'question,correct_answer\n"unclosed,A\n', b"question,correct_answer\nx,A,extra\n", b"question,correct_answer\n\n"):
            with self.subTest(data=data):
                self.assertTrue(parse_quiz_csv(data).errors)

    def test_header_only_template_is_not_a_valid_import(self):
        from app.parsers.quiz_csv_parser import parse_quiz_csv
        result = parse_quiz_csv(b"question,correct_answer\n")
        self.assertEqual(result.row_count, 0)
        self.assertTrue(result.errors)

    def test_renamed_binary_files_are_rejected(self):
        from app.parsers.quiz_csv_parser import parse_quiz_csv
        for prefix in (b"PK\x03\x04", b"%PDF-", b"MZ", b"\x7fELF", b"\x89PNG"):
            self.assertTrue(parse_quiz_csv(prefix + b"question,correct_answer\nx,A\n").errors)


class QuizImportTokenChecks(unittest.TestCase):
    def test_confirmation_is_bound_to_owner_file_signature_and_expiry(self):
        from app.services.quiz_import import create_preview_token, verify_preview_token
        from app.parsers.quiz_csv_parser import QuizImportError
        token = create_preview_token(USER, b"reviewed bytes", secret="test-secret", now=1000)
        verify_preview_token(token, USER, b"reviewed bytes", secret="test-secret", now=1899)
        for owner, data, now, secret in ((SUBJECT, b"reviewed bytes", 1100, "test-secret"), (USER, b"changed bytes", 1100, "test-secret"), (USER, b"reviewed bytes", 1900, "test-secret"), (USER, b"reviewed bytes", 1100, "wrong-secret")):
            with self.assertRaises(QuizImportError) as raised:
                verify_preview_token(token, owner, data, secret=secret, now=now)
            self.assertEqual(raised.exception.status_code, 422)
        for invalid in ("", "private.invalid", token + ".extra", token[:-1] + "!"):
            with self.assertRaises(QuizImportError):
                verify_preview_token(invalid, USER, b"reviewed bytes", secret="test-secret", now=1100)

    def test_missing_signing_secret_fails_closed(self):
        from app.services.quiz_import import create_preview_token
        from app.parsers.quiz_csv_parser import QuizImportError
        with self.assertRaises(QuizImportError) as raised:
            create_preview_token(USER, b"file", secret="")
        self.assertEqual(raised.exception.status_code, 503)


class QuizImportPreviewChecks(unittest.TestCase):
    def report(self, data, existing=None, catalog=None):
        from app.services import quiz_import
        catalog = catalog or {"subjects": [{"id": SUBJECT, "code": "MAS"}], "topics": [{"id": TOPIC, "subject_id": SUBJECT, "code": "MS-1"}]}
        def existing_questions(connection, owner, identities):
            self.assertEqual(owner, USER)
            return {identity: existing for identity in identities} if existing else {}
        with patch.object(quiz_import.repo, "import_catalog", return_value=catalog), patch.object(quiz_import.repo, "find_import_questions", side_effect=existing_questions), patch.object(quiz_import.quiz_service, "validate_question_associations"):
            return quiz_import.build_preview(object(), USER, data)

    def test_subject_alias_topic_mapping_tf_and_multiselect_normalize(self):
        data = csv_bytes([
            {"subject": "MS", "topic": "MS-1", "question": "  Tax   principle ", "question_type": "true_false", "correct_answer": "TRUE"},
            {"question": "Pick both", "question_type": "multi_select", "option_a": "One", "option_b": "Two", "correct_answer": "B;A"},
        ], ["subject", "topic", "question", "question_type", "option_a", "option_b", "correct_answer"])
        result, inserts = self.report(data)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["proposed_inserts"], 2)
        self.assertEqual(result["sample"][0]["subject_id"], str(SUBJECT))
        self.assertEqual(result["sample"][0]["topic_id"], str(TOPIC))
        self.assertEqual(result["sample"][0]["prompt"], "Tax principle")
        self.assertEqual(result["sample"][0]["options"], [{"key": "TRUE", "text": "True"}, {"key": "FALSE", "text": "False"}])
        self.assertEqual(result["sample"][1]["correct_keys"], ["A", "B"])

    def test_invalid_mappings_types_keys_and_sources_are_row_errors(self):
        variants = [{"subject": "UNKNOWN"}, {"topic": "MS-1"}, {"subject": "MS", "topic": "missing"}, {"question_type": "essay"}, {"correct_answer": "C"}, {"correct_answer": "A;B"}, {"option_b": "One"}, {"resource_id": "not-a-uuid"}, {"source_page": "0"}, {"question_type": "true_false"}]
        for variant in variants:
            row = {"question": "Question", "option_a": "One", "option_b": "Two", "correct_answer": "A", **variant}
            result, _ = self.report(csv_bytes([row], sorted(row)))
            self.assertTrue(result["errors"], variant)
        ambiguous = {"subjects": [{"id": SUBJECT, "code": "MAS"}], "topics": [{"id": TOPIC, "subject_id": SUBJECT, "code": "MS-1"}] * 2}
        result, _ = self.report(csv_bytes([{"subject": "MS", "topic": "MS-1", "question": "x", "option_a": "1", "option_b": "2", "correct_answer": "A"}], ["subject", "topic", "question", "option_a", "option_b", "correct_answer"]), catalog=ambiguous)
        self.assertTrue(result["errors"])

    def test_exact_file_duplicates_skip_and_conflicting_identity_blocks(self):
        row = {"question": "Question", "option_a": "One", "option_b": "Two", "correct_answer": "A"}
        result, inserts = self.report(csv_bytes([row, {**row, "question": " Question  "}]))
        self.assertEqual((result["proposed_inserts"], result["unchanged"], result["duplicate_count"]), (1, 1, 1))
        self.assertEqual(len(inserts), 1)
        self.assertEqual(result["warnings"][0]["row"], 3)
        conflict, _ = self.report(csv_bytes([row, {**row, "correct_answer": "B"}]))
        self.assertTrue(conflict["errors"])
        self.assertEqual(conflict["errors"][0]["row"], 3)

    def test_existing_exact_payload_is_unchanged_and_changed_payload_conflicts(self):
        from app.schemas.quizzes import QuestionInput
        from app.repositories.quizzes import question_hashes
        row = {"question": "Question", "option_a": "One", "option_b": "Two", "correct_answer": "A"}
        _, content_hash = question_hashes(QuestionInput(question_type="single_select", prompt="Question", options=[{"key": "A", "text": "One"}, {"key": "B", "text": "Two"}], correct_keys=["A"]))
        result, inserts = self.report(csv_bytes([row]), existing={"content_hash": content_hash})
        self.assertEqual((result["proposed_inserts"], result["unchanged"]), (0, 1))
        self.assertEqual(inserts, [])
        conflict, _ = self.report(csv_bytes([row]), existing={"content_hash": "different"})
        self.assertTrue(conflict["errors"])

    def test_sample_is_limited_to_twenty_rows(self):
        result, inserts = self.report(csv_bytes([{"question": f"Question {i}", "option_a": "1", "option_b": "2", "correct_answer": "A"} for i in range(21)]))
        self.assertEqual(len(result["sample"]), 20)
        self.assertEqual(len(inserts), 21)

    def test_extreme_source_page_is_a_row_error(self):
        result, _ = self.report(csv_bytes([{"question": "Question", "option_a": "One", "option_b": "Two", "correct_answer": "A", "source_page": "9" * 9999}], ["question", "option_a", "option_b", "correct_answer", "source_page"]))
        self.assertTrue(result["errors"])
        self.assertEqual(result["errors"][0]["field"], "source_page")


class QuizImportCommitChecks(unittest.TestCase):
    def test_commit_revalidates_all_rows_before_inserting_and_rerun_is_unchanged(self):
        from app.services import quiz_import
        rows = {}
        operations = []
        data = csv_bytes([{"question": "Question", "option_a": "One", "option_b": "Two", "correct_answer": "A"}])
        secret = "test-secret"
        token = quiz_import.create_preview_token(USER, data, secret=secret)

        @contextmanager
        def memory_transaction():
            before = dict(rows)
            try:
                yield object()
            except Exception:
                rows.clear()
                rows.update(before)
                raise

        def insert(connection, owner, entries, *, origin):
            self.assertEqual(owner, USER)
            self.assertEqual(origin, "csv")
            for question, identity_hash, content_hash in entries:
                operations.append("insert")
                rows[identity_hash] = {"content_hash": content_hash}

        def existing_questions(connection, owner, identities):
            self.assertEqual(owner, USER)
            return {identity: rows[identity] for identity in identities if identity in rows}

        with patch.object(quiz_import, "_secret", return_value=secret.encode()), patch.object(quiz_import.repo, "transaction", memory_transaction), patch.object(quiz_import.repo, "lock_import_owner", side_effect=lambda *args: operations.append("lock")), patch.object(quiz_import.repo, "import_catalog", return_value={"subjects": [], "topics": []}), patch.object(quiz_import.repo, "find_import_questions", side_effect=existing_questions), patch.object(quiz_import.repo, "insert_questions", side_effect=insert), patch.object(quiz_import.quiz_service, "validate_question_associations"):
            self.assertEqual(quiz_import.commit_questions(USER, data, token), {"inserted": 1, "unchanged": 0})
            self.assertEqual(quiz_import.commit_questions(USER, data, token), {"inserted": 0, "unchanged": 1})
            changed = csv_bytes([{"question": "Question", "option_a": "One", "option_b": "Two", "correct_answer": "B"}])
            changed_token = quiz_import.create_preview_token(USER, changed, secret=secret)
            with self.assertRaises(quiz_import.QuizImportError):
                quiz_import.commit_questions(USER, changed, changed_token)
        self.assertEqual(len(rows), 1)
        self.assertEqual(operations, ["lock", "insert", "lock", "lock"])

    def test_error_in_later_row_blocks_entire_commit_and_preview_never_inserts(self):
        from app.services import quiz_import
        secret = "test-secret"
        data = csv_bytes([{"question": "Valid", "option_a": "One", "option_b": "Two", "correct_answer": "A"}, {"question": "Invalid", "option_a": "One", "option_b": "Two", "correct_answer": "F"}])
        token = quiz_import.create_preview_token(USER, data, secret=secret)
        def forbidden(*args, **kwargs):
            raise AssertionError("Preview or invalid import performed a write")
        with patch.object(quiz_import, "_secret", return_value=secret.encode()), patch.object(quiz_import.repo, "transaction", transaction), patch.object(quiz_import.repo, "lock_import_owner"), patch.object(quiz_import.repo, "import_catalog", return_value={"subjects": [], "topics": []}), patch.object(quiz_import.repo, "find_import_questions", return_value={}), patch.object(quiz_import.repo, "insert_questions", side_effect=forbidden), patch.object(quiz_import.quiz_service, "validate_question_associations"):
            preview = quiz_import.preview_questions(USER, data)
            self.assertTrue(preview["errors"])
            self.assertIsNone(preview["preview_token"])
            with self.assertRaises(quiz_import.QuizImportError):
                quiz_import.commit_questions(USER, data, token)

    def test_later_insert_constraint_failure_rolls_back_all_questions(self):
        from sqlalchemy.exc import IntegrityError
        from app.services import quiz_import
        persisted = []
        data = csv_bytes([{"question": f"Question {i}", "option_a": "One", "option_b": "Two", "correct_answer": "A"} for i in range(2)])
        secret = "test-secret"
        token = quiz_import.create_preview_token(USER, data, secret=secret)

        @contextmanager
        def memory_transaction():
            try:
                yield object()
            except Exception:
                persisted.clear()
                raise

        def insert(connection, owner, entries, **kwargs):
            for question, identity_hash, content_hash in entries:
                if persisted:
                    raise IntegrityError("insert", {}, ValueError("private conflict"))
                persisted.append(question)

        with patch.object(quiz_import, "_secret", return_value=secret.encode()), patch.object(quiz_import.repo, "transaction", memory_transaction), patch.object(quiz_import.repo, "lock_import_owner"), patch.object(quiz_import.repo, "import_catalog", return_value={"subjects": [], "topics": []}), patch.object(quiz_import.repo, "find_import_questions", return_value={}), patch.object(quiz_import.repo, "insert_questions", side_effect=insert), patch.object(quiz_import.quiz_service, "validate_question_associations"):
            with self.assertRaises(quiz_import.QuizImportError) as raised:
                quiz_import.commit_questions(USER, data, token)
        self.assertEqual(raised.exception.status_code, 409)
        self.assertEqual(persisted, [])


class QuizImportApiChecks(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        import httpx
        from fastapi import FastAPI
        from app.api.quiz_import import router, QuestionImportBodyLimit
        self.app = FastAPI()
        self.app.include_router(router)
        self.app.add_middleware(QuestionImportBodyLimit)
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app), base_url="http://test")

    async def asyncTearDown(self):
        await self.client.aclose()

    def signed_in(self):
        from app.core.auth import get_current_user
        from app.schemas.auth import AuthenticatedUser
        self.app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id=USER, email=None)

    async def test_routes_require_auth_and_reject_extra_duplicate_or_missing_fields(self):
        for path in ("preview", "commit"):
            response = await self.client.post("/api/imports/questions/" + path)
            self.assertEqual(response.status_code, 401)
        self.signed_in()
        for fields in ({"user_id": str(USER)}, {"preview_token": "extra"}, {"file": "wrong"}):
            response = await self.client.post("/api/imports/questions/preview", data=fields, files={"file": ("test.csv", b"question,correct_answer\n", "text/csv")})
            self.assertEqual(response.status_code, 422)
        response = await self.client.post("/api/imports/questions/commit", files={"file": ("test.csv", b"question,correct_answer\n", "text/csv")})
        self.assertEqual(response.status_code, 422)

    async def test_request_is_bounded_before_multipart_parsing_with_or_without_length(self):
        self.signed_in()
        response = await self.client.post("/api/imports/questions/preview", files={"file": ("test.csv", b"x" * (1048576 + 1), "text/csv")})
        self.assertEqual(response.status_code, 413)

    async def test_only_matching_csv_extension_and_mime_are_supported(self):
        self.signed_in()
        safe_report = {"row_count": 0, "valid_count": 0, "duplicate_count": 0, "proposed_inserts": 0, "unchanged": 0, "warnings": [], "errors": [], "sample": [], "preview_token": None}
        with patch("app.services.quiz_import.preview_questions", return_value=safe_report):
            for name, mime in (("test.pdf", "text/csv"), ("test.csv", "application/pdf"), ("test", "text/csv"), ("test.csv", "application/octet-stream")):
                response = await self.client.post("/api/imports/questions/preview", files={"file": (name, b"question,correct_answer\n", mime)})
                self.assertEqual(response.status_code, 415, (name, mime))
        async def body():
            for _ in range(20):
                yield b"x" * 65536
        response = await self.client.post("/api/imports/questions/commit", content=body(), headers={"Content-Type": "multipart/form-data; boundary=x"})
        self.assertEqual(response.status_code, 413)

    async def test_malformed_upload_and_dependency_failures_are_safe(self):
        from sqlalchemy.exc import SQLAlchemyError
        self.signed_in()
        response = await self.client.post("/api/imports/questions/preview", content=b"private form body", headers={"Content-Type": "multipart/form-data; boundary=x"})
        self.assertEqual(response.status_code, 422)
        self.assertNotIn("private", response.text)
        with patch("app.services.quiz_import.preview_questions", side_effect=SQLAlchemyError("private database connection")):
            response = await self.client.post("/api/imports/questions/preview", files={"file": ("test.csv", b"question,correct_answer\n", "text/csv")})
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("private", response.text)


if __name__ == "__main__":
    unittest.main()
