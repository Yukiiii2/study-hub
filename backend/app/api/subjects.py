from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID

from app.core.auth import CurrentUser
from app.repositories.subjects import get_subject, list_subjects
from app.repositories.topics import list_topics
from app.schemas.topics import TopicResponse
from app.schemas.subjects import SubjectResponse

router = APIRouter(prefix="/api/subjects", tags=["subjects"])


@router.get("", response_model=list[SubjectResponse])
def subjects(user: CurrentUser) -> list[SubjectResponse]:
    try:
        return list_subjects()
    except (SQLAlchemyError, ValueError):
        raise HTTPException(status_code=503, detail="Study data is unavailable. Check database setup.") from None


@router.get("/{subject_id}", response_model=SubjectResponse)
def subject_detail(subject_id: UUID, user: CurrentUser) -> SubjectResponse:
    try:
        subject = get_subject(subject_id)
    except (SQLAlchemyError, ValueError):
        raise HTTPException(status_code=503, detail="Study data is unavailable. Check database setup.") from None
    if subject is None:
        raise HTTPException(status_code=404, detail="Subject not found.")
    return subject


@router.get("/{subject_id}/topics", response_model=list[TopicResponse])
def subject_topics(subject_id: UUID, user: CurrentUser) -> list[TopicResponse]:
    try:
        if get_subject(subject_id) is None:
            raise HTTPException(status_code=404, detail="Subject not found.")
        return list_topics(subject_id)
    except (SQLAlchemyError, ValueError):
        raise HTTPException(status_code=503, detail="Study data is unavailable. Check database setup.") from None
