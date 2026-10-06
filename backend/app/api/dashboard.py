from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.core.auth import CurrentUser
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard import get_dashboard
from app.services.planner_recurrence import PlannerError

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(user: CurrentUser) -> DashboardResponse:
    try:
        return get_dashboard(user.id)
    except (SQLAlchemyError, ValueError, PlannerError):
        raise HTTPException(status_code=503, detail="Dashboard data is unavailable. Try again.") from None
