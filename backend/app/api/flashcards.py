from functools import wraps
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Response
from sqlalchemy.exc import SQLAlchemyError

from app.core.auth import CurrentUser
from app.schemas.flashcards import (CardCreate, CardList, CardPatch, CardResponse, DeckCreate,
                                    DeckList, DeckPatch, DeckResponse, DueList, ReviewInput,
                                    ReviewList, ReviewResponse)
from app.services import flashcards as service

router = APIRouter(prefix="/api", tags=["flashcards"])


def boundary(handler):
    @wraps(handler)
    def guarded(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except service.FlashcardError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from None
        except (SQLAlchemyError, ValueError, OverflowError):
            raise HTTPException(status_code=503, detail="Flashcards are unavailable. Try again.") from None
    return guarded


@router.get("/flashcard-decks", response_model=DeckList)
@boundary
def deck_list(user: CurrentUser, subject_id: UUID | None = None,
              q: Annotated[str | None, Query(max_length=200)] = None,
              limit: Annotated[int, Query(ge=1, le=100)] = 50,
              offset: Annotated[int, Query(ge=0)] = 0):
    return service.list_decks(user.id, subject_id=subject_id, q=q, limit=limit, offset=offset)


@router.post("/flashcard-decks", response_model=DeckResponse, status_code=201)
@boundary
def deck_create(data: DeckCreate, user: CurrentUser):
    return service.create_deck(user.id, data)


@router.get("/flashcard-decks/{deck_id}", response_model=DeckResponse)
@boundary
def deck_get(deck_id: UUID, user: CurrentUser):
    return service.get_deck(user.id, deck_id)


@router.patch("/flashcard-decks/{deck_id}", response_model=DeckResponse)
@boundary
def deck_patch(deck_id: UUID, data: DeckPatch, user: CurrentUser):
    return service.patch_deck(user.id, deck_id, data)


@router.delete("/flashcard-decks/{deck_id}", status_code=204)
@boundary
def deck_delete(deck_id: UUID, user: CurrentUser):
    service.delete_deck(user.id, deck_id)
    return Response(status_code=204)


@router.get("/flashcards", response_model=CardList)
@boundary
def card_list(user: CurrentUser, subject_id: UUID | None = None, topic_id: UUID | None = None,
              deck_id: UUID | None = None, resource_id: UUID | None = None,
              status: Literal["active", "suspended", "archived", "all"] = "active",
              q: Annotated[str | None, Query(max_length=200)] = None,
              limit: Annotated[int, Query(ge=1, le=100)] = 50,
              offset: Annotated[int, Query(ge=0)] = 0):
    return service.list_cards(user.id, subject_id=subject_id, topic_id=topic_id, deck_id=deck_id,
                              resource_id=resource_id, status=status, q=q, limit=limit, offset=offset)


@router.post("/flashcards", response_model=CardResponse, status_code=201)
@boundary
def card_create(data: CardCreate, user: CurrentUser):
    return service.create_card(user.id, data)


@router.get("/flashcards/due", response_model=DueList)
@boundary
def card_due(user: CurrentUser, subject_id: UUID | None = None, deck_id: UUID | None = None,
             mode: Literal["due", "overdue", "today", "upcoming"] = "due",
             limit: Annotated[int, Query(ge=1, le=100)] = 50,
             offset: Annotated[int, Query(ge=0)] = 0):
    return service.due_cards(user.id, subject_id=subject_id, deck_id=deck_id, mode=mode, limit=limit, offset=offset)


@router.get("/flashcards/{card_id}", response_model=CardResponse)
@boundary
def card_get(card_id: UUID, user: CurrentUser):
    return service.get_card(user.id, card_id)


@router.patch("/flashcards/{card_id}", response_model=CardResponse)
@boundary
def card_patch(card_id: UUID, data: CardPatch, user: CurrentUser):
    return service.patch_card(user.id, card_id, data)


@router.delete("/flashcards/{card_id}", status_code=204)
@boundary
def card_delete(card_id: UUID, user: CurrentUser):
    service.delete_card(user.id, card_id)
    return Response(status_code=204)


@router.post("/flashcards/{card_id}/review", response_model=ReviewResponse)
@boundary
def card_review(card_id: UUID, data: ReviewInput, user: CurrentUser):
    return service.review_card(user.id, card_id, data)


@router.get("/flashcards/{card_id}/reviews", response_model=ReviewList)
@boundary
def card_reviews(card_id: UUID, user: CurrentUser,
                 limit: Annotated[int, Query(ge=1, le=100)] = 50,
                 offset: Annotated[int, Query(ge=0)] = 0):
    return service.list_reviews(user.id, card_id, limit=limit, offset=offset)
