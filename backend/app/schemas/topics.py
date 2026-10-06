from uuid import UUID

from pydantic import BaseModel


class TopicResponse(BaseModel):
    id: UUID
    subject_id: UUID
    parent_topic_id: UUID | None
    code: str | None
    title: str
    description: str | None
    display_order: int
