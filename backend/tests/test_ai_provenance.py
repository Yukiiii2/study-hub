"""Focused draft-receipt integrity and explicit-save boundary checks."""
import base64
import hashlib
import hmac
import json
import unittest
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import uuid4

from pydantic import SecretStr, ValidationError

from app.ai import draft_receipts as receipts
from app.repositories import quizzes as question_repo
from app.repositories import flashcards as card_repo
from app.schemas.ai_provenance import AIProvenanceDTO
from app.schemas.flashcards import CardCreate, CardPatch
from app.schemas.quizzes import QuestionInput, QuestionResponse
from app.services import flashcards, quizzes

NOW = datetime(2026, 10, 9, 12, tzinfo=timezone.utc)


@contextmanager
def transaction():
    yield object()


def question(**updates):
    values = dict(question_type="single_select", prompt="User edited question?",
                  options=[{"key": "A", "text": "One"}, {"key": "B", "text": "Two"}], correct_keys=["A"])
    return QuestionInput(**{**values, **updates})


class ReceiptChecks(unittest.TestCase):
    def setUp(self):
        self.user = uuid4()
        self.source = uuid4()
        self.settings = patch.object(receipts, "get_settings", return_value=SimpleNamespace(
            supabase_secret_key=SecretStr("sb_secret_test_only")))
        self.clock = patch.object(receipts, "_now", return_value=NOW)
        self.settings.start()
        self.clock.start()
        self.addCleanup(self.settings.stop)
        self.addCleanup(self.clock.stop)

    def mint(self, kind="question", **updates):
        return receipts.mint_draft_receipt(self.user, kind, provider="gemini", model="test-model",
                                          generated_at=NOW, **updates)

    def test_receipt_preserves_original_source_and_uses_separate_key(self):
        topic, subject, attempt, qid = [uuid4() for _ in range(4)]
        token = self.mint("flashcard", subject_id=subject, topic_id=topic, resource_id=self.source,
                          source_pages=[2, 4], attempt_id=attempt, question_id=qid)
        provenance = receipts.verify_draft_receipt(token, self.user, "flashcard")
        self.assertEqual(provenance.resource_id, self.source)
        self.assertEqual(provenance.source_pages, [2, 4])
        self.assertEqual(provenance.attempt_id, attempt)
        payload, signature = token.split(".")
        raw = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
        self.assertEqual(raw["expires_at"] - raw["issued_at"], 86400)
        self.assertEqual(set(raw), {"version", "user_id", "kind", "issued_at", "expires_at", "provenance"})
        direct = receipts._encode(hmac.digest(b"sb_secret_test_only", payload.encode(), "sha256"))
        self.assertNotEqual(signature, direct)
        self.assertNotIn("sb_secret", token)

    def test_tampering_foreign_owner_wrong_kind_malformed_and_expiry_fail_generically(self):
        token = self.mint()
        cases = [(token, uuid4(), "question"), (token, self.user, "flashcard"),
                 (token[:-1] + ("a" if token[-1] != "a" else "b"), self.user, "question"),
                 ("!bad", self.user, "question"), ("a" * 2049, self.user, "question")]
        for value, user, kind in cases:
            with self.subTest(kind=kind), self.assertRaises(receipts.DraftReceiptError) as caught:
                receipts.verify_draft_receipt(value, user, kind)
            self.assertEqual(caught.exception.status_code, 400)
            self.assertNotIn(value, caught.exception.detail)
        for at in (NOW - timedelta(seconds=1), NOW + timedelta(hours=24)):
            with patch.object(receipts, "_now", return_value=at), self.assertRaises(receipts.DraftReceiptError):
                receipts.verify_draft_receipt(token, self.user, "question")

    def test_strict_metadata_bounds_and_empty_secret(self):
        for updates in ({"source_pages": [1]}, {"resource_id": self.source, "source_pages": [True]},
                        {"resource_id": self.source, "source_pages": [1, 1]},
                        {"resource_id": self.source, "source_pages": list(range(1, 8))},
                        {"attempt_id": uuid4()}, {"topic_id": uuid4()}):
            with self.subTest(updates=updates), self.assertRaises(receipts.DraftReceiptError):
                self.mint(**updates)
        with self.assertRaises(ValidationError):
            AIProvenanceDTO(provider="gemini", model="test", generated_at=NOW, raw_prompt="private")
        with patch.object(receipts, "get_settings", return_value=SimpleNamespace(supabase_secret_key=SecretStr(""))):
            with self.assertRaises(receipts.DraftReceiptError) as caught:
                self.mint()
            self.assertEqual(caught.exception.status_code, 503)

    def test_signed_but_invalid_schema_and_lifetime_are_rejected(self):
        token = self.mint()
        payload = token.split(".")[0]
        original = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
        for update in ({"expires_at": original["expires_at"] + 1}, {"raw_prompt": "private"}, {"version": True}):
            raw = {**original, **update}
            signed_payload = receipts._encode(json.dumps(raw).encode())
            signed = signed_payload + "." + receipts._encode(hmac.digest(
                receipts._signing_key(), signed_payload.encode(), "sha256"))
            with self.assertRaises(receipts.DraftReceiptError):
                receipts.verify_draft_receipt(signed, self.user, "question")

    def test_client_cannot_supply_provenance_or_origin_and_receipt_is_not_serialized(self):
        token = self.mint()
        for schema, values in ((QuestionInput, question().model_dump()), (CardCreate, {"front": "Front", "back": "Back"})):
            for extra in ({"ai_provenance": {}}, {"origin": "ai"}, {"ai_draft_receipt": "a" * 2049}):
                with self.assertRaises(ValidationError):
                    schema.model_validate({**values, **extra})
            draft = schema.model_validate({**values, "ai_draft_receipt": token})
            self.assertNotIn("ai_draft_receipt", draft.model_dump())
        with self.assertRaises(ValidationError):
            CardPatch(ai_draft_receipt=token)
        qresponse = QuestionResponse(**question().model_dump(), id=uuid4(), origin="ai",
                                     ai_provenance=receipts.verify_draft_receipt(token, self.user, "question"),
                                     is_archived=False, created_at=NOW, updated_at=NOW)
        self.assertNotIn("ai_draft_receipt", qresponse.model_dump())

    def test_hashes_preserve_manual_csv_fingerprint_even_with_ai_metadata(self):
        plain = question()
        draft = question(ai_draft_receipt=self.mint())
        payload = plain.model_dump(mode="json")
        payload["options"] = sorted(payload["options"], key=lambda option: option["key"])
        legacy_digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"),
                                                 ensure_ascii=False).encode()).hexdigest()
        self.assertEqual(question_repo.question_hashes(plain)[1], legacy_digest)
        self.assertEqual(question_repo.question_hashes(plain), question_repo.question_hashes(draft))

    def test_confirmed_question_save_stores_signed_origin_after_content_edits(self):
        token = self.mint(resource_id=self.source, source_pages=[3])
        repo = Mock(transaction=transaction, find_import_question=Mock(return_value=None),
                    question_hashes=question_repo.question_hashes)
        draft = question(ai_draft_receipt=token)
        with patch.object(quizzes, "repo", repo):
            quizzes.create_question(self.user, draft)
        args, kwargs = repo.insert_question.call_args
        self.assertEqual(args[2].prompt, "User edited question?")
        self.assertEqual(kwargs["origin"], "ai")
        self.assertEqual(kwargs["ai_provenance"]["resource_id"], str(self.source))
        self.assertEqual(kwargs["ai_provenance"]["source_pages"], [3])
        self.assertIsNone(args[2].resource_id)
        repo.valid_resource.assert_called_once()
        with patch.object(quizzes, "repo", repo), self.assertRaises(quizzes.QuizError):
            quizzes.create_question(uuid4(), draft)
        self.assertEqual(repo.insert_question.call_count, 1)

    def test_ai_card_saves_suspended_manual_card_remains_active(self):
        def insert(connection, kind, user, values, *, now):
            return {**values, "id": uuid4(), "interval_days": 0, "next_review_at": now,
                    "review_revision": 0, "created_at": now, "updated_at": now}
        repo = Mock(transaction=transaction, insert_record=Mock(side_effect=insert))
        token = self.mint("flashcard")
        with patch.object(flashcards, "repo", repo), patch.object(flashcards, "_now", return_value=NOW):
            ai_card = flashcards.create_card(self.user, CardCreate(front="Edited front", back="Edited back",
                                                                  status="active", ai_draft_receipt=token))
            manual = flashcards.create_card(self.user, CardCreate(front="Front", back="Back"))
        self.assertEqual(ai_card["status"], "suspended")
        self.assertEqual(ai_card["ai_provenance"]["provider"], "gemini")
        self.assertNotIn("ai_draft_receipt", ai_card)
        self.assertEqual(manual["status"], "active")
        self.assertIsNone(manual["ai_provenance"])
        self.assertNotIn("ai_draft_receipt", repo.insert_record.call_args.args[3])

    def test_question_update_without_new_receipt_preserves_origin(self):
        qid = uuid4()
        repo = Mock(transaction=transaction, get_question=Mock(return_value={"is_archived": False}),
                    find_import_question=Mock(return_value=None), question_hashes=question_repo.question_hashes)
        with patch.object(quizzes, "repo", repo):
            quizzes.patch_question(self.user, qid, question())
        self.assertEqual(repo.update_question.call_args.kwargs, {})

    def test_persistence_uses_jsonb_and_never_writes_receipts(self):
        provenance = receipts.verify_draft_receipt(self.mint(), self.user, "question").model_dump(mode="json")
        connection = Mock()
        qid = uuid4()
        connection.execute.return_value.scalar_one.return_value = qid
        with patch.object(question_repo, "_write_options"), patch.object(question_repo, "get_question"):
            question_repo.insert_question(connection, self.user, question(ai_draft_receipt=self.mint()),
                                          origin="ai", ai_provenance=provenance)
            sql, values = connection.execute.call_args.args
            self.assertIn("CAST(:ai_provenance AS jsonb)", str(sql))
            self.assertEqual(json.loads(values["ai_provenance"]), provenance)
            self.assertNotIn("ai_draft_receipt", values)
            connection.reset_mock()
            question_repo.update_question(connection, self.user, qid, question(), ai_provenance=provenance)
            sql, values = connection.execute.call_args_list[0].args
            self.assertIn("ai_provenance=CAST(:ai_provenance AS jsonb)", str(sql))
            self.assertEqual(values["origin"], "ai")
            self.assertIn("WHERE user_id=:user_id AND id=:id", str(sql))
        connection.reset_mock()
        connection.execute.return_value.mappings.return_value.one.return_value = {"id": qid}
        card_repo.insert_record(connection, "card", self.user,
                                {"front": "Front", "back": "Back", "status": "suspended",
                                 "ai_provenance": provenance, "ai_draft_receipt": "must not persist"}, now=NOW)
        sql, values = connection.execute.call_args.args
        self.assertIn("CAST(:ai_provenance AS jsonb)", str(sql))
        self.assertEqual(json.loads(values["ai_provenance"]), provenance)
        self.assertNotIn("ai_draft_receipt", values)

    def test_ai_card_can_only_enter_active_queue_by_existing_explicit_update(self):
        token = self.mint("flashcard")
        provenance = receipts.verify_draft_receipt(token, self.user, "flashcard").model_dump(mode="json")
        card_id = uuid4()
        row = {**CardCreate(front="Front", back="Back", status="suspended").model_dump(),
               "ai_provenance": provenance, "id": card_id, "interval_days": 0, "next_review_at": NOW,
               "review_revision": 0, "created_at": NOW, "updated_at": NOW}
        def update(connection, kind, user, record_id, values):
            return {**row, **values, "review_revision": 1}
        repo = Mock(transaction=transaction, get_record=Mock(return_value=row),
                    update_record=Mock(side_effect=update))
        with patch.object(flashcards, "repo", repo):
            result = flashcards.patch_card(self.user, card_id, CardPatch(status="active"))
        self.assertEqual(result["status"], "active")
        self.assertEqual(result["ai_provenance"]["provider"], "gemini")
        self.assertEqual(repo.update_record.call_args.args[4], {"status": "active"})


if __name__ == "__main__":
    unittest.main()
