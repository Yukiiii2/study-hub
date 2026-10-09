from datetime import date
from enum import IntEnum
from functools import wraps

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError

from app.core.auth import CurrentUser
from app.schemas.analytics import AnalyticsResponse, SessionHistoryResponse
from app.services import analytics as service
from app.services.planner_recurrence import PlannerError

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


class Period(IntEnum):
    week = 7
    month = 30
    quarter = 90


def boundary(handler):
    @wraps(handler)
    def guarded(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except PlannerError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from None
        except (SQLAlchemyError, ValueError):
            raise HTTPException(status_code=503, detail="Analytics data is unavailable. Try again.") from None
    return guarded


@router.get("/summary", response_model=AnalyticsResponse)
@boundary
def summary(user: CurrentUser, period: Period = Period.week,
            start_date: date | None = None, end_date: date | None = None):
    return service.get_summary(user.id, period, start_date, end_date)


@router.get("/sessions", response_model=SessionHistoryResponse)
@boundary
def sessions(user: CurrentUser, period: Period = Period.week,
             start_date: date | None = None, end_date: date | None = None,
             limit: int = Query(default=20, ge=1, le=100), offset: int = Query(default=0, ge=0)):
    return service.get_sessions(user.id, period, start_date, end_date, limit, offset)
