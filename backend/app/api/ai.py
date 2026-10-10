from typing import Annotated, Callable

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.ai.errors import AIError
from app.ai.provider import get_provider
from app.core.auth import CurrentUser
from app.schemas.ai import (AskInput, GenerateQuizInput, GenerateCardsInput, ExplainInput,
                            AnswerResponse, QuizDraftResponse, CardsDraftResponse)
from app.services.ai_study import study

router = APIRouter(prefix="/api/ai", tags=["AI study assistance"])


def get_provider_factory():
    return get_provider


ProviderFactory = Annotated[Callable, Depends(get_provider_factory)]


async def _run(user_id, data, action, factory):
    try:
        return await study(user_id, data, action, factory)
    except AIError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from None
    except (SQLAlchemyError, ValueError):
        raise HTTPException(status_code=503, detail="AI study context is unavailable. Try again.") from None


@router.post("/ask", response_model=AnswerResponse)
async def ask(data: AskInput, user: CurrentUser, factory: ProviderFactory):
    return await _run(user.id, data, "ask", factory)


@router.post("/generate-quiz", response_model=QuizDraftResponse)
async def generate_quiz(data: GenerateQuizInput, user: CurrentUser, factory: ProviderFactory):
    return await _run(user.id, data, "generate-quiz", factory)


@router.post("/generate-flashcards", response_model=CardsDraftResponse)
async def generate_flashcards(data: GenerateCardsInput, user: CurrentUser, factory: ProviderFactory):
    return await _run(user.id, data, "generate-flashcards", factory)


@router.post("/explain-answer", response_model=AnswerResponse)
async def explain_answer(data: ExplainInput, user: CurrentUser, factory: ProviderFactory):
    return await _run(user.id, data, "explain-answer", factory)
