"""Focused recall scheduling, input, ownership and locked lifecycle checks."""
import importlib.util
import unittest
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from uuid import uuid4

from pydantic import ValidationError

NOW = datetime(2026, 10, 9, 12, tzinfo=timezone.utc)


class ScheduleChecks(unittest.TestCase):
    def test_backend_schedule_exists(self):
        self.assertIsNotNone(importlib.util.find_spec("app.services.recall_schedule"), "Recall scheduler is missing")

    def test_exact_first_review_intervals_and_again(self):
        from app.services.recall_schedule import schedule_review
        for rating, days in (("hard", 1), ("good", 1), ("easy", 4)):
            result = schedule_review(0, rating, NOW)
            self.assertEqual(result["next_interval_days"], days)
            self.assertEqual(result["next_review_at"], NOW + timedelta(days=days))
        again = schedule_review(30, "again", NOW)
        self.assertEqual(again["next_interval_days"], 0)
        self.assertEqual(again["next_review_at"], NOW + timedelta(minutes=10))

    def test_ceiling_growth_cap_and_aware_server_time(self):
        from app.services.recall_schedule import schedule_review
        for interval, rating, expected in ((1, "hard", 2), (3, "hard", 4), (3, "good", 8), (3, "easy", 11), (365, "easy", 365)):
            self.assertEqual(schedule_review(interval, rating, NOW)["next_interval_days"], expected)
        for interval, rating, now in ((-1, "good", NOW), (366, "good", NOW), (1, "unknown", NOW), (1, "good", NOW.replace(tzinfo=None)), (True, "good", NOW)):
            with self.subTest(interval=interval, rating=rating), self.assertRaises(ValueError):
                schedule_review(interval, rating, now)


class SchemaChecks(unittest.TestCase):
    def test_card_inputs_reject_client_schedule_and_invalid_associations(self):
        from app.schemas.flashcards import CardCreate, CardPatch, ReviewInput
        for extra in ({"interval_days": 4}, {"review_revision": 9}, {"user_id": uuid4()}, {"next_review_at": NOW}, {"topic_id": uuid4()}, {"source_page": 1}, {"front": " "}, {"back": "Bad\x00"}):
            with self.subTest(extra=extra), self.assertRaises(ValidationError):
                CardCreate.model_validate({"front": "Front", "back": "Back", **extra})
        for extra in ({"front": None}, {"back": None}, {"status": None}, {"review_revision": 1}):
            with self.subTest(extra=extra), self.assertRaises(ValidationError):
                CardPatch.model_validate(extra)
        valid = CardPatch.model_validate({"notes": None, "deck_id": None})
        self.assertEqual(valid.model_dump(exclude_unset=True), {"deck_id": None, "notes": None})
        for revision in (-1, True, 1.5):
            with self.subTest(revision=revision), self.assertRaises(ValidationError):
                ReviewInput(rating="good", expected_revision=revision, request_id=uuid4())

    def test_deck_patch_is_partial_and_title_cannot_be_cleared(self):
        from app.schemas.flashcards import DeckCreate, DeckPatch
        self.assertEqual(DeckPatch(description=None).model_dump(exclude_unset=True), {"description": None})
        for data in ({"title": None}, {"title": " "}, {"title": "Line\nTitle"}, {"is_archived": True}):
            with self.subTest(data=data), self.assertRaises(ValidationError):
                DeckPatch.model_validate(data)
        with self.assertRaises(ValidationError):
            DeckCreate(title="Deck", description="Bad\x1b")


class CardStore:
    """Database boundary stand-in retains transaction rollback and owned state."""
    def __init__(self):
        self.user = uuid4()
        self.cards = {}
        self.decks = {}
        self.reviews = {}
        self.locks = []
        self.fail_review = False

    @contextmanager
    def transaction(self):
        saved = deepcopy((self.cards, self.decks, self.reviews))
        try:
            yield object()
        except Exception:
            self.cards, self.decks, self.reviews = saved
            raise

    def get_record(self, connection, kind, user_id, record_id, *, lock=None):
        self.locks.append((kind, record_id, lock))
        rows = self.cards if kind == "card" else self.decks
        return deepcopy(rows.get(record_id)) if user_id == self.user else None

    def valid_associations(self, connection, subject_id, topic_id):
        return topic_id is None or subject_id is not None

    def valid_resource(self, connection, user_id, resource_id, source_page):
        return resource_id is None and source_page is None

    def insert_record(self, connection, kind, user_id, data, *, now=None):
        row = {**data, "id": uuid4(), "created_at": NOW, "updated_at": NOW}
        if kind == "card":
            row.update(interval_days=0, next_review_at=now, review_revision=0)
            self.cards[row["id"]] = row
        else:
            row["is_archived"] = False
            self.decks[row["id"]] = row
        return deepcopy(row)

    def update_record(self, connection, kind, user_id, record_id, data):
        row = (self.cards if kind == "card" else self.decks)[record_id]
        row.update(data)
        if kind == "card" and data:
            row["review_revision"] += 1
        return deepcopy(row)

    def archive_card(self, connection, user_id, card_id):
        row = self.cards[card_id]
        if row["status"] != "archived":
            row.update(status="archived", review_revision=row["review_revision"] + 1)

    def archive_deck(self, connection, user_id, deck_id):
        self.decks[deck_id]["is_archived"] = True
        for card in self.cards.values():
            if card["deck_id"] == deck_id:
                card.update(deck_id=None, review_revision=card["review_revision"] + 1)

    def deck_subject_conflicts(self, connection, user_id, deck_id, subject_id):
        return subject_id is not None and any(c["deck_id"] == deck_id and c["subject_id"] != subject_id for c in self.cards.values())

    def review_by_request(self, connection, user_id, request_id):
        return deepcopy(self.reviews.get(request_id))

    def insert_review(self, connection, user_id, data):
        from sqlalchemy.exc import IntegrityError
        if self.fail_review:
            raise IntegrityError("private SQL", {}, Exception("private payload"))
        row = {**data, "id": uuid4(), "created_at": NOW}
        self.reviews[data["request_id"]] = row
        return deepcopy(row)

    def apply_review(self, connection, user_id, card_id, interval_days, next_review_at):
        row = self.cards[card_id]
        row.update(interval_days=interval_days, next_review_at=next_review_at, review_revision=row["review_revision"] + 1)

    def list_reviews(self, connection, user_id, card_id, **filters):
        rows = [deepcopy(r) for r in self.reviews.values() if r["flashcard_id"] == card_id]
        return {"reviews": rows, "total": len(rows)}


class CardLifecycleChecks(unittest.TestCase):
    def setUp(self):
        from app.services import flashcards as service
        from app.schemas.flashcards import CardCreate
        self.service = service
        self.store = CardStore()
        self.repo_patch = patch.object(service, "repo", self.store)
        self.clock_patch = patch.object(service, "_now", return_value=NOW)
        self.repo_patch.start()
        self.clock_patch.start()
        self.addCleanup(self.repo_patch.stop)
        self.addCleanup(self.clock_patch.stop)
        self.card = service.create_card(self.store.user, CardCreate(front="Original front", back="Original back"))

    def test_new_card_is_due_now_and_partial_content_edit_keeps_schedule(self):
        from app.schemas.flashcards import CardPatch
        card = self.card
        self.assertEqual((card["interval_days"], card["next_review_at"], card["review_revision"]), (0, NOW, 0))
        changed = self.service.patch_card(self.store.user, card["id"], CardPatch(front="Edited front"))
        self.assertEqual(changed["front"], "Edited front")
        self.assertEqual(changed["back"], "Original back")
        self.assertEqual((changed["interval_days"], changed["next_review_at"], changed["review_revision"]), (0, NOW, 1))
        unchanged = self.service.patch_card(self.store.user, card["id"], CardPatch(front="Edited front"))
        self.assertEqual(unchanged["review_revision"], 1)

    def test_exact_retry_returns_one_frozen_review_after_edit_and_archive(self):
        from app.schemas.flashcards import CardPatch, ReviewInput
        data = ReviewInput(rating="good", expected_revision=0, request_id=uuid4())
        review = self.service.review_card(self.store.user, self.card["id"], data)
        self.assertEqual(review["next_review_at"], NOW + timedelta(days=1))
        self.assertEqual(self.store.cards[self.card["id"]]["review_revision"], 1)
        self.service.patch_card(self.store.user, self.card["id"], CardPatch(back="Changed back"))
        self.service.delete_card(self.store.user, self.card["id"])
        retry = self.service.review_card(self.store.user, self.card["id"], data)
        self.assertEqual(retry, review)
        self.assertEqual(len(self.store.reviews), 1)
        history = self.service.list_reviews(self.store.user, self.card["id"])
        self.assertEqual(history["reviews"][0]["back_snapshot"], "Original back")
        self.assertNotIn("user_id", review)

    def test_stale_edit_reused_request_and_non_due_card_are_conflicts(self):
        from app.schemas.flashcards import CardPatch, ReviewInput
        service = self.service
        data = ReviewInput(rating="good", expected_revision=0, request_id=uuid4())
        service.patch_card(self.store.user, self.card["id"], CardPatch(notes="Changed"))
        with self.assertRaises(service.FlashcardError) as stale:
            service.review_card(self.store.user, self.card["id"], data)
        self.assertEqual(stale.exception.status_code, 409)
        data.expected_revision = 1
        service.review_card(self.store.user, self.card["id"], data)
        with self.assertRaises(service.FlashcardError) as reused:
            service.review_card(self.store.user, self.card["id"], ReviewInput(rating="easy", expected_revision=1, request_id=data.request_id))
        self.assertEqual(reused.exception.status_code, 409)
        with self.assertRaises(service.FlashcardError) as future:
            service.review_card(self.store.user, self.card["id"], ReviewInput(rating="easy", expected_revision=2, request_id=uuid4()))
        self.assertEqual(future.exception.status_code, 409)
        self.assertEqual(len(self.store.reviews), 1)

    def test_suspended_archived_and_foreign_cards_cannot_be_reviewed(self):
        from app.schemas.flashcards import CardPatch, ReviewInput
        for status in ("suspended", "archived"):
            card = self.service.patch_card(self.store.user, self.card["id"], CardPatch(status=status))
            with self.assertRaises(self.service.FlashcardError) as conflict:
                self.service.review_card(self.store.user, card["id"], ReviewInput(rating="again", expected_revision=card["review_revision"], request_id=uuid4()))
            self.assertEqual(conflict.exception.status_code, 409)
        with self.assertRaises(self.service.FlashcardError) as foreign:
            self.service.get_card(uuid4(), self.card["id"])
        self.assertEqual(foreign.exception.status_code, 404)
        self.assertEqual(self.store.reviews, {})


    def test_deck_subject_conflict_and_delete_detach_preserve_card(self):
        from app.schemas.flashcards import CardPatch, DeckCreate, DeckPatch
        deck = self.service.create_deck(self.store.user, DeckCreate(title="Deck"))
        attached = self.service.patch_card(self.store.user, self.card["id"], CardPatch(deck_id=deck["id"]))
        with self.assertRaises(self.service.FlashcardError) as conflict:
            self.service.patch_deck(self.store.user, deck["id"], DeckPatch(subject_id=uuid4()))
        self.assertEqual(conflict.exception.status_code, 409)
        self.service.delete_deck(self.store.user, deck["id"])
        retained = self.service.get_card(self.store.user, attached["id"])
        self.assertIsNone(retained["deck_id"])
        self.assertEqual(retained["front"], attached["front"])
        self.assertEqual(retained["next_review_at"], attached["next_review_at"])
        self.assertTrue(self.store.decks[deck["id"]]["is_archived"])
        self.assertEqual(retained["status"], "active")

    def test_review_constraint_failure_rolls_back_and_has_safe_conflict(self):
        from app.schemas.flashcards import ReviewInput
        self.store.fail_review = True
        with self.assertRaises(self.service.FlashcardError) as caught:
            self.service.review_card(self.store.user, self.card["id"], ReviewInput(rating="easy", expected_revision=0, request_id=uuid4()))
        self.assertEqual(caught.exception.status_code, 409)
        self.assertNotIn("private", caught.exception.detail)
        self.assertEqual(self.store.cards[self.card["id"]]["review_revision"], 0)
        self.assertEqual(self.store.reviews, {})

    def test_resource_locks_precede_card_update_lock_when_editing(self):
        from app.schemas.flashcards import CardPatch
        old, new = uuid4(), uuid4()
        self.store.cards[self.card["id"]].update(resource_id=old, source_page=1)
        def lock_resource(connection, user_id, resource_id, source_page):
            if resource_id is not None:
                self.store.locks.append(("resource", resource_id, "share"))
            return True
        with patch.object(self.store, "valid_resource", side_effect=lock_resource):
            result = self.service.patch_card(self.store.user, self.card["id"], CardPatch(resource_id=new))
        self.assertEqual(result["resource_id"], new)
        self.assertIn(("resource", old, "share"), self.store.locks)
        update_index = self.store.locks.index(("card", self.card["id"], "update"))
        self.assertLess(self.store.locks.index(("resource", old, "share")), update_index)
        self.assertLess(self.store.locks.index(("resource", new, "share")), update_index)


class QueryResult:
    def __init__(self, rows):
        self.rows = rows

    def mappings(self):
        return self

    def all(self):
        return self.rows

    def one(self):
        return self.rows[0]

    def first(self):
        return self.rows[0] if self.rows else None

    def scalar_one(self):
        return len(self.rows)

    def __iter__(self):
        return iter(self.rows)


class QueryConnection:
    def __init__(self):
        self.calls = []
        self.cards = [{"id": uuid4()} for _ in range(100)]

    def execute(self, query, params):
        sql = str(query)
        self.calls.append((sql, params))
        if "FILTER" in sql:
            return QueryResult([{"overdue": 5, "due_today": 10, "upcoming": 85}])
        return QueryResult(self.cards)


class QueryChecks(unittest.TestCase):
    def test_hundred_card_list_is_two_queries_with_owner_and_safe_search(self):
        from app.repositories import flashcards as repo
        connection = QueryConnection()
        user = uuid4()
        result = repo.list_cards(connection, user, limit=100, status="all", q="%_\\")
        self.assertEqual(len(connection.calls), 2)
        self.assertEqual(len(result["cards"]), 100)
        self.assertEqual(result["total"], 100)
        for sql, params in connection.calls:
            self.assertIn("user_id=:user_id", sql)
            self.assertNotIn("status=:status", sql)
            self.assertEqual(params["user_id"], user)
            self.assertEqual(params["q"], "%\\%\\_\\\\%")

    def test_due_modes_use_actual_due_time_active_owner_and_two_queries(self):
        from app.repositories import flashcards as repo
        day_start = NOW.replace(hour=0)
        user, deck = uuid4(), uuid4()
        for mode, total, condition in (("due", 15, "next_review_at<=:now"), ("overdue", 5, "next_review_at<:day_start"),
                                       ("today", 10, "next_review_at>=:day_start AND next_review_at<=:now"),
                                       ("upcoming", 85, "next_review_at>:now")):
            with self.subTest(mode=mode):
                connection = QueryConnection()
                result = repo.due_cards(connection, user, NOW, day_start, mode=mode, deck_id=deck, limit=100)
                self.assertEqual(result["total"], total)
                self.assertEqual(len(connection.calls), 2)
                sql, params = connection.calls[-1]
                self.assertIn(condition, sql)
                self.assertIn("ORDER BY next_review_at,id", sql)
                self.assertIn("user_id=:user_id", sql)
                self.assertIn("deck_id=:deck_id", sql)
                self.assertEqual((params["user_id"], params["status"], params["now"], params["deck_id"]), (user, "active", NOW, deck))

    def test_card_lock_and_request_lookup_are_always_owner_bound(self):
        from app.repositories import flashcards as repo
        connection = QueryConnection()
        user, card, request = uuid4(), uuid4(), uuid4()
        repo.get_record(connection, "card", user, card, lock="update")
        repo.review_by_request(connection, user, request)
        sql, params = connection.calls[0]
        self.assertIn("WHERE user_id=:user_id AND id=:id FOR UPDATE", sql)
        self.assertEqual(params, {"user_id": user, "id": card})
        sql, params = connection.calls[1]
        self.assertIn("WHERE user_id=:user_id AND request_id=:request_id", sql)
        self.assertEqual(params, {"user_id": user, "request_id": request})

    def test_queue_local_day_uses_profile_zone_including_dst_boundary(self):
        from app.services import flashcards as service
        @contextmanager
        def transaction():
            yield object()
        cases = (("Asia/Taipei", NOW, datetime(2026, 10, 8, 16, tzinfo=timezone.utc)),
                 ("America/New_York", datetime(2026, 11, 1, 12, tzinfo=timezone.utc), datetime(2026, 11, 1, 4, tzinfo=timezone.utc)))
        for zone, now, expected_start in cases:
            def read_queue(connection, user_id, server_now, day_start, **filters):
                self.assertEqual((server_now, day_start), (now, expected_start))
                return {"cards": [], "total": 0, "summary": {"overdue": 0, "due_today": 0, "upcoming": 0}}
            with self.subTest(zone=zone), patch.object(service.repo, "transaction", transaction), patch.object(service.repo, "profile_timezone", return_value=zone), patch.object(service.repo, "due_cards", side_effect=read_queue), patch.object(service, "_now", return_value=now):
                result = service.due_cards(uuid4())
            self.assertEqual((result["timezone"], result["as_of"]), (zone, now))


class ApiChecks(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        import httpx
        from fastapi import FastAPI
        from app.api.flashcards import router
        from app.core.auth import get_current_user
        from app.schemas.auth import AuthenticatedUser
        from app.services import flashcards as service
        self.store = CardStore()
        self.service = service
        self.app = FastAPI()
        self.app.include_router(router)
        self.app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id=self.store.user, email=None)
        self.repo_patch = patch.object(service, "repo", self.store)
        self.clock_patch = patch.object(service, "_now", return_value=NOW)
        self.repo_patch.start()
        self.clock_patch.start()
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app), base_url="http://test")

    async def asyncTearDown(self):
        await self.client.aclose()
        self.repo_patch.stop()
        self.clock_patch.stop()

    async def test_create_review_contract_and_no_client_schedule(self):
        created = await self.client.post("/api/flashcards", json={"front": "Front", "back": "Back"})
        self.assertEqual(created.status_code, 201)
        card = created.json()
        self.assertNotIn("user_id", card)
        data = {"rating": "easy", "expected_revision": card["review_revision"], "request_id": str(uuid4())}
        reviewed = await self.client.post(f"/api/flashcards/{card['id']}/review", json=data)
        self.assertEqual(reviewed.status_code, 200)
        result = reviewed.json()
        self.assertEqual(result["next_interval_days"], 4)
        self.assertEqual(result["front_snapshot"], "Front")
        self.assertNotIn("card", result)
        self.assertNotIn("review", result)
        self.assertNotIn("user_id", result)
        retried = await self.client.post(f"/api/flashcards/{card['id']}/review", json=data)
        self.assertEqual(retried.json(), result)
        invalid = await self.client.post("/api/flashcards", json={"front": "Front", "back": "Back", "next_review_at": NOW.isoformat()})
        self.assertEqual(invalid.status_code, 422)

    async def test_foreign_missing_and_safe_dependency_failure(self):
        from sqlalchemy.exc import SQLAlchemyError
        missing = await self.client.get(f"/api/flashcards/{uuid4()}")
        self.assertEqual(missing.status_code, 404)
        with patch.object(self.service, "list_cards", side_effect=SQLAlchemyError("private database locator")):
            response = await self.client.get("/api/flashcards")
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("private database locator", response.text)
