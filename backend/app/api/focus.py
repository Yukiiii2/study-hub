from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.core.auth import CurrentUser
from app.schemas.focus import FocusResponse
from app.services import focus as service
from app.services.planner_recurrence import PlannerError

router = APIRouter(prefix="/api", tags=["focus"])


@router.get("/focus", response_model=FocusResponse)
def focus(user: CurrentUser) -> FocusResponse:
    try:
        return service.get_focus(user.id)
    except (SQLAlchemyError, ValueError, PlannerError):
        raise HTTPException(status_code=503, detail="Focus data is unavailable. Try again.") from None
