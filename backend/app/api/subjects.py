from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.core.auth import CurrentUser
from app.repositories.subjects import list_subjects
from app.schemas.subjects import SubjectResponse

router = APIRouter(prefix="/api/subjects", tags=["subjects"])


@router.get("", response_model=list[SubjectResponse])
def subjects(user: CurrentUser) -> list[SubjectResponse]:
    try:
        return list_subjects()
    except (SQLAlchemyError, ValueError):
        raise HTTPException(status_code=503, detail="Study data is unavailable. Check database setup.") from None
