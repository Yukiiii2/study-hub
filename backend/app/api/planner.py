from datetime import date
from functools import wraps
from uuid import UUID

from fastapi import APIRouter, HTTPException, Response
from pydantic import AwareDatetime
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.auth import CurrentUser
from app.schemas.planner import (
    EventCreate, EventPatch, EventResponse, OccurrencePatch, OccurrenceResponse,
    PlannerContext, SessionCreate, SessionPatch, SessionResponse, TaskCreate, TaskPatch, TaskResponse,
)
from app.services import planner as service
from app.services.planner_recurrence import PlannerError

router = APIRouter(prefix="/api", tags=["study planner"])


def boundary(handler):
    @wraps(handler)
    def guarded(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except PlannerError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from None
        except IntegrityError as error:
            state = getattr(error.orig, "sqlstate", None)
            if state == "23505":
                raise HTTPException(status_code=409, detail="This action conflicts with an existing schedule or active session.") from None
            if state in {"23503", "23514"}:
                raise HTTPException(status_code=422, detail="Invalid planner values or relationships.") from None
            raise HTTPException(status_code=503, detail="Planner data is unavailable. Try again.") from None
        except (SQLAlchemyError, ValueError):
            raise HTTPException(status_code=503, detail="Planner data is unavailable. Try again.") from None
    return guarded


@router.get("/study-plan/context", response_model=PlannerContext)
@boundary
def context(user: CurrentUser):
    return service.get_context(user.id)


@router.get("/study-events", response_model=list[OccurrenceResponse])
@boundary
def events(user: CurrentUser, start_at: AwareDatetime, end_at: AwareDatetime):
    return service.list_events(user.id, start_at, end_at)


@router.post("/study-events", response_model=EventResponse, status_code=201)
@boundary
def event_create(body: EventCreate, user: CurrentUser):
    return service.create_event(user.id, body)


@router.get("/study-events/{event_id}", response_model=EventResponse)
@boundary
def event_get(event_id: UUID, user: CurrentUser):
    return service.required(service.get_event(user.id, event_id), "Event")


@router.patch("/study-events/{event_id}", response_model=EventResponse)
@boundary
def event_patch(event_id: UUID, body: EventPatch, user: CurrentUser):
    return service.patch_event(user.id, event_id, body)


@router.delete("/study-events/{event_id}", status_code=204)
@boundary
def event_delete(event_id: UUID, user: CurrentUser):
    service.delete_event(user.id, event_id)
    return Response(status_code=204)


@router.patch("/study-events/{event_id}/occurrences/{occurrence_date}", response_model=OccurrenceResponse)
@boundary
def occurrence_patch(event_id: UUID, occurrence_date: date, body: OccurrencePatch, user: CurrentUser):
    return service.patch_occurrence(user.id, event_id, occurrence_date, body)


@router.delete("/study-events/{event_id}/occurrences/{occurrence_date}", status_code=204)
@boundary
def occurrence_delete(event_id: UUID, occurrence_date: date, user: CurrentUser):
    service.patch_occurrence(user.id, event_id, occurrence_date, deleted=True)
    return Response(status_code=204)


@router.get("/study-tasks", response_model=list[TaskResponse])
@boundary
def tasks(user: CurrentUser):
    return service.list_tasks(user.id)


@router.post("/study-tasks", response_model=TaskResponse, status_code=201)
@boundary
def task_create(body: TaskCreate, user: CurrentUser):
    return service.create_task(user.id, body)


@router.patch("/study-tasks/{task_id}", response_model=TaskResponse)
@boundary
def task_patch(task_id: UUID, body: TaskPatch, user: CurrentUser):
    return service.patch_task(user.id, task_id, body)


@router.delete("/study-tasks/{task_id}", status_code=204)
@boundary
def task_delete(task_id: UUID, user: CurrentUser):
    service.delete_task(user.id, task_id)
    return Response(status_code=204)


@router.post("/study-tasks/{task_id}/schedule", response_model=EventResponse, status_code=201)
@boundary
def task_schedule(task_id: UUID, body: EventCreate, user: CurrentUser):
    return service.schedule_task(user.id, task_id, body)


@router.get("/study-sessions", response_model=list[SessionResponse])
@boundary
def sessions(user: CurrentUser, start_at: AwareDatetime | None = None, end_at: AwareDatetime | None = None):
    return service.list_sessions(user.id, start_at, end_at)


@router.post("/study-sessions", response_model=SessionResponse, status_code=201)
@boundary
def session_create(body: SessionCreate, user: CurrentUser):
    return service.create_session(user.id, body)


@router.patch("/study-sessions/{session_id}", response_model=SessionResponse)
@boundary
def session_patch(session_id: UUID, body: SessionPatch, user: CurrentUser):
    return service.patch_session(user.id, session_id, body)
