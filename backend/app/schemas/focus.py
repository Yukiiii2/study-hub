from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.analytics import LabeledSessionResponse
from app.schemas.planner import SessionResponse


class FocusResponse(BaseModel):
    timezone: str
    server_now: datetime
    active_session: SessionResponse | None
    today_seconds: int = Field(ge=0)
    today_session_count: int = Field(ge=0)
    recent_sessions: list[LabeledSessionResponse] = Field(max_length=10)
