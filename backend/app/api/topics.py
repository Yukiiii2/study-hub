from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.core.auth import CurrentUser
from app.repositories.topics import get_topic
from app.schemas.topics import TopicResponse

router = APIRouter(prefix="/api/topics", tags=["topics"])


@router.get("/{topic_id}", response_model=TopicResponse)
def topic_detail(topic_id: UUID, user: CurrentUser) -> TopicResponse:
    try:
        topic = get_topic(topic_id)
    except (SQLAlchemyError, ValueError):
        raise HTTPException(status_code=503, detail="Study data is unavailable. Check database setup.") from None
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found.")
    return topic
