from functools import wraps
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Response
from sqlalchemy.exc import SQLAlchemyError

from app.core.auth import CurrentUser
from app.schemas.assessments import (AssessmentCreate, AssessmentDetail, AssessmentList,
                                    AssessmentPatch, AssessmentResponse, AttemptCreate,
                                    AttemptList, AttemptPatch, AttemptResponse)
from app.services import assessments as service

router = APIRouter(prefix="/api", tags=["assessments"])


def boundary(handler):
    @wraps(handler)
    def guarded(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except service.AssessmentError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from None
        except (SQLAlchemyError, ValueError, OverflowError):
            raise HTTPException(status_code=503, detail="Assessments are unavailable. Try again.") from None
    return guarded


@router.get("/assessments", response_model=AssessmentList)
@boundary
def assessment_list(user: CurrentUser,
                    status: Literal["all", "planned", "completed", "cancelled", "archived"] = "all",
                    q: Annotated[str | None, Query(max_length=200)] = None,
                    limit: Annotated[int, Query(ge=1, le=100)] = 50,
                    offset: Annotated[int, Query(ge=0)] = 0):
    return service.list_assessments(user.id, status=status, q=q, limit=limit, offset=offset)


@router.post("/assessments", response_model=AssessmentResponse, status_code=201)
@boundary
def assessment_create(data: AssessmentCreate, user: CurrentUser):
    return service.create_assessment(user.id, data)


@router.get("/assessments/{assessment_id}", response_model=AssessmentDetail)
@boundary
def assessment_get(assessment_id: UUID, user: CurrentUser):
    return service.get_assessment(user.id, assessment_id)


@router.patch("/assessments/{assessment_id}", response_model=AssessmentResponse)
@boundary
def assessment_patch(assessment_id: UUID, data: AssessmentPatch, user: CurrentUser):
    return service.patch_assessment(user.id, assessment_id, data)


@router.delete("/assessments/{assessment_id}", status_code=204)
@boundary
def assessment_delete(assessment_id: UUID, user: CurrentUser):
    service.delete_assessment(user.id, assessment_id)
    return Response(status_code=204)


@router.post("/assessments/{assessment_id}/attempts", response_model=AttemptResponse, status_code=201)
@boundary
def attempt_create(assessment_id: UUID, data: AttemptCreate, user: CurrentUser):
    return service.create_attempt(user.id, assessment_id, data)


@router.get("/assessments/{assessment_id}/attempts", response_model=AttemptList)
@boundary
def attempt_list(assessment_id: UUID, user: CurrentUser,
                 limit: Annotated[int, Query(ge=1, le=100)] = 50,
                 offset: Annotated[int, Query(ge=0)] = 0):
    return service.list_attempts(user.id, assessment_id, limit=limit, offset=offset)


@router.patch("/assessment-attempts/{attempt_id}", response_model=AttemptResponse)
@boundary
def attempt_patch(attempt_id: UUID, data: AttemptPatch, user: CurrentUser):
    return service.patch_attempt(user.id, attempt_id, data)
