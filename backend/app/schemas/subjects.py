from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SubjectResponse(BaseModel):
    id: UUID
    code: str
    name: str
    display_order: int
    color_key: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
