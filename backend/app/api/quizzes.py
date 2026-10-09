from functools import wraps
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError

from app.core.auth import CurrentUser
from app.schemas.quizzes import (AnswerInput, ArchiveInput, AttemptList, AttemptResponse,
                                QuestionInput, QuestionList, QuestionResponse, QuestionType,
                                QuizDetail, QuizInput, QuizList)
from app.services import quizzes as service

router = APIRouter(prefix="/api", tags=["quizzes"])


def boundary(handler):
    @wraps(handler)
    def guarded(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except service.QuizError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from None
        except (SQLAlchemyError, ValueError):
            raise HTTPException(status_code=503, detail="Quizzes are unavailable. Try again.") from None
    return guarded


@router.get("/questions", response_model=QuestionList)
@boundary
def question_list(user: CurrentUser, subject_id: UUID | None = None, topic_id: UUID | None = None,
                  resource_id: UUID | None = None, question_type: QuestionType | None = None,
                  q: Annotated[str | None, Query(max_length=200)] = None,
                  limit: Annotated[int, Query(ge=1, le=100)] = 50,
                  offset: Annotated[int, Query(ge=0)] = 0):
    return service.list_questions(user.id, subject_id=subject_id, topic_id=topic_id, resource_id=resource_id,
                                  question_type=question_type, q=q, limit=limit, offset=offset)


@router.post("/questions", response_model=QuestionResponse, status_code=201)
@boundary
def question_create(data: QuestionInput, user: CurrentUser):
    return service.create_question(user.id, data)


@router.get("/questions/{question_id}", response_model=QuestionResponse)
@boundary
def question_get(question_id: UUID, user: CurrentUser):
    return service.get_question(user.id, question_id)


@router.patch("/questions/{question_id}", response_model=QuestionResponse)
@boundary
def question_patch(question_id: UUID, data: QuestionInput | ArchiveInput, user: CurrentUser):
    return service.patch_question(user.id, question_id, data)


@router.get("/quizzes", response_model=QuizList)
@boundary
def quiz_list(user: CurrentUser, subject_id: UUID | None = None,
              q: Annotated[str | None, Query(max_length=200)] = None,
              limit: Annotated[int, Query(ge=1, le=100)] = 50,
              offset: Annotated[int, Query(ge=0)] = 0):
    return service.list_quizzes(user.id, subject_id=subject_id, q=q, limit=limit, offset=offset)


@router.post("/quizzes", response_model=QuizDetail, status_code=201)
@boundary
def quiz_create(data: QuizInput, user: CurrentUser):
    return service.create_quiz(user.id, data)


@router.get("/quizzes/{quiz_id}", response_model=QuizDetail)
@boundary
def quiz_get(quiz_id: UUID, user: CurrentUser):
    return service.get_quiz(user.id, quiz_id)


@router.patch("/quizzes/{quiz_id}", response_model=QuizDetail)
@boundary
def quiz_patch(quiz_id: UUID, data: QuizInput | ArchiveInput, user: CurrentUser):
    return service.patch_quiz(user.id, quiz_id, data)


@router.post("/quizzes/{quiz_id}/attempts", response_model=AttemptResponse)
@boundary
def attempt_start(quiz_id: UUID, user: CurrentUser):
    return service.start_attempt(user.id, quiz_id)


@router.get("/quiz-attempts", response_model=AttemptList)
@boundary
def attempt_list(user: CurrentUser, quiz_id: UUID | None = None,
                 limit: Annotated[int, Query(ge=1, le=100)] = 50,
                 offset: Annotated[int, Query(ge=0)] = 0):
    return service.list_attempts(user.id, quiz_id=quiz_id, limit=limit, offset=offset)


@router.get("/quiz-attempts/{attempt_id}", response_model=AttemptResponse)
@boundary
def attempt_get(attempt_id: UUID, user: CurrentUser):
    return service.get_attempt(user.id, attempt_id)


@router.post("/quiz-attempts/{attempt_id}/answers", response_model=AttemptResponse)
@boundary
def answer_save(attempt_id: UUID, data: AnswerInput, user: CurrentUser):
    return service.save_answer(user.id, attempt_id, data)


@router.post("/quiz-attempts/{attempt_id}/complete", response_model=AttemptResponse)
@boundary
def attempt_complete(attempt_id: UUID, user: CurrentUser):
    return service.complete_attempt(user.id, attempt_id)


@router.get("/quiz-attempts/{attempt_id}/results", response_model=AttemptResponse)
@boundary
def attempt_results(attempt_id: UUID, user: CurrentUser):
    return service.get_attempt(user.id, attempt_id, results=True)
