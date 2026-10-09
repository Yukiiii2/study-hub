"""Server-owned card state and serialized, retry-safe recall review transactions."""
from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.repositories import flashcards as repo
from app.schemas.flashcards import (CardCreate, CardList, CardResponse, DeckCreate, DeckList,
                                    DeckResponse, DueList, ReviewList, ReviewResponse)
from app.services.recall_schedule import schedule_review


class FlashcardError(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def _now():
    return datetime.now(timezone.utc)


def _required(row, kind):
    if row is None:
        raise FlashcardError(404, f"{kind} not found.")
    return row


def _response(schema, row):
    return schema.model_validate(row).model_dump()


def _merged(schema, current, patch):
    values = {key: current[key] for key in schema.model_fields}
    values.update(patch.model_dump(exclude_unset=True))
    try:
        return schema.model_validate(values)
    except ValidationError:
        raise FlashcardError(422, "Invalid flashcard fields or associations.") from None


def _lock_decks(connection, user_id, deck_ids):
    return {deck_id: _required(repo.get_record(connection, "deck", user_id, deck_id, lock="share"), "Deck")
            for deck_id in sorted({value for value in deck_ids if value is not None})}


def _validate_card(connection, user_id, data, decks):
    if not repo.valid_associations(connection, data.subject_id, data.topic_id):
        raise FlashcardError(422, "Choose an active subject and its matching topic.")
    if not repo.valid_resource(connection, user_id, data.resource_id, data.source_page):
        raise FlashcardError(422, "Choose an owned resource and an existing PDF source page.")
    if data.deck_id is not None:
        deck = decks[data.deck_id]
        if deck["is_archived"]:
            raise FlashcardError(409, "Archived decks cannot accept cards.")
        if deck["subject_id"] is not None and deck["subject_id"] != data.subject_id:
            raise FlashcardError(422, "Card subject must match the selected deck's subject.")


def list_decks(user_id, **filters):
    with repo.transaction() as connection:
        return _response(DeckList, repo.list_decks(connection, user_id, **filters))


def get_deck(user_id, deck_id):
    with repo.transaction() as connection:
        return _response(DeckResponse, _required(repo.get_record(connection, "deck", user_id, deck_id), "Deck"))


def create_deck(user_id, data):
    with repo.transaction() as connection:
        if not repo.valid_associations(connection, data.subject_id, None):
            raise FlashcardError(422, "Choose an active subject.")
        return _response(DeckResponse, repo.insert_record(connection, "deck", user_id, data.model_dump()))


def patch_deck(user_id, deck_id, patch):
    with repo.transaction() as connection:
        current = _required(repo.get_record(connection, "deck", user_id, deck_id, lock="update"), "Deck")
        data = _merged(DeckCreate, current, patch)
        if not repo.valid_associations(connection, data.subject_id, None):
            raise FlashcardError(422, "Choose an active subject.")
        if data.subject_id != current["subject_id"] and repo.deck_subject_conflicts(connection, user_id, deck_id, data.subject_id):
            raise FlashcardError(409, "Deck subject conflicts with its assigned cards.")
        changed = {key: value for key, value in patch.model_dump(exclude_unset=True).items() if current[key] != value}
        return _response(DeckResponse, repo.update_record(connection, "deck", user_id, deck_id, changed))


def delete_deck(user_id, deck_id):
    with repo.transaction() as connection:
        _required(repo.get_record(connection, "deck", user_id, deck_id, lock="update"), "Deck")
        repo.archive_deck(connection, user_id, deck_id)


def list_cards(user_id, **filters):
    with repo.transaction() as connection:
        return _response(CardList, repo.list_cards(connection, user_id, **filters))


def get_card(user_id, card_id):
    with repo.transaction() as connection:
        return _response(CardResponse, _required(repo.get_record(connection, "card", user_id, card_id), "Card"))


def create_card(user_id, data):
    with repo.transaction() as connection:
        decks = _lock_decks(connection, user_id, [data.deck_id])
        _validate_card(connection, user_id, data, decks)
        return _response(CardResponse, repo.insert_record(connection, "card", user_id, data.model_dump(), now=_now()))


def patch_card(user_id, card_id, patch):
    with repo.transaction() as connection:
        before = _required(repo.get_record(connection, "card", user_id, card_id), "Card")
        # Deck and source locks precede card locks, matching their detach paths.
        decks = _lock_decks(connection, user_id, [before["deck_id"], patch.deck_id])
        resources = {value for value in (before["resource_id"], patch.resource_id) if value is not None}
        for resource_id in sorted(resources):
            if not repo.valid_resource(connection, user_id, resource_id, None):
                if resource_id == before["resource_id"]:
                    raise FlashcardError(409, "Card source changed. Reload this card before editing.")
                raise FlashcardError(422, "Choose an owned resource.")
        current = _required(repo.get_record(connection, "card", user_id, card_id, lock="update"), "Card")
        if current["deck_id"] != before["deck_id"] or current["resource_id"] != before["resource_id"]:
            raise FlashcardError(409, "Card associations changed. Reload this card before editing.")
        data = _merged(CardCreate, current, patch)
        _validate_card(connection, user_id, data, decks)
        changed = {key: value for key, value in patch.model_dump(exclude_unset=True).items() if current[key] != value}
        return _response(CardResponse, repo.update_record(connection, "card", user_id, card_id, changed))


def delete_card(user_id, card_id):
    with repo.transaction() as connection:
        _required(repo.get_record(connection, "card", user_id, card_id, lock="update"), "Card")
        repo.archive_card(connection, user_id, card_id)


def due_cards(user_id, **filters):
    with repo.transaction() as connection:
        timezone_name = repo.profile_timezone(connection, user_id)
        try:
            zone = ZoneInfo(timezone_name)
        except (ZoneInfoNotFoundError, ValueError, TypeError):
            raise FlashcardError(503, "Recall timezone is unavailable. Try again.") from None
        now = _now()
        day_start = datetime.combine(now.astimezone(zone).date(), time.min, tzinfo=zone).astimezone(timezone.utc)
        result = repo.due_cards(connection, user_id, now, day_start, **filters)
        return _response(DueList, {**result, "timezone": timezone_name, "as_of": now})


def review_card(user_id, card_id, data):
    try:
        with repo.transaction() as connection:
            card = _required(repo.get_record(connection, "card", user_id, card_id, lock="update"), "Card")
            previous = repo.review_by_request(connection, user_id, data.request_id)
            if previous is not None:
                if (previous["flashcard_id"] != card_id or previous["rating"] != data.rating or
                        previous["previous_revision"] != data.expected_revision):
                    raise FlashcardError(409, "Review request identity conflicts with a previous review.")
                return _response(ReviewResponse, previous)
            if card["review_revision"] != data.expected_revision:
                raise FlashcardError(409, "This card changed after it was loaded. Reload before reviewing.")
            now = _now()
            if card["status"] != "active" or card["next_review_at"] > now:
                raise FlashcardError(409, "Only active cards that are due can be reviewed.")
            scheduled = schedule_review(card["interval_days"], data.rating, now)
            review = repo.insert_review(connection, user_id, {"flashcard_id": card_id, "request_id": data.request_id,
                         "previous_revision": card["review_revision"], "reviewed_at": now, "rating": data.rating,
                         "previous_interval_days": card["interval_days"], **scheduled,
                         "front_snapshot": card["front"], "back_snapshot": card["back"]})
            repo.apply_review(connection, user_id, card_id, scheduled["next_interval_days"], scheduled["next_review_at"])
            return _response(ReviewResponse, review)
    except IntegrityError:
        raise FlashcardError(409, "Review conflicts with current history. Reload this card before reviewing.") from None


def list_reviews(user_id, card_id, **filters):
    with repo.transaction() as connection:
        _required(repo.get_record(connection, "card", user_id, card_id), "Card")
        return _response(ReviewList, repo.list_reviews(connection, user_id, card_id, **filters))
