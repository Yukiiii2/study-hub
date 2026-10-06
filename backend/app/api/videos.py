from uuid import UUID
from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.core.auth import CurrentUser
from app.repositories.subjects import get_subject
from app.repositories.topics import get_topic
from app.repositories.videos import list_videos, update_progress
from app.schemas.videos import ProgressUpdate, SubjectVideosResponse, VideoResponse
from app.services.video_tracking import summarize

router = APIRouter(prefix="/api", tags=["videos"])


@router.get("/topics/{topic_id}/videos", response_model=list[VideoResponse])
def topic_videos(topic_id: UUID, user: CurrentUser) -> list[VideoResponse]:
    try:
        if get_topic(topic_id) is None:
            raise HTTPException(status_code=404, detail="Topic not found.")
        return list_videos(user.id, topic_id=topic_id)
    except (SQLAlchemyError, ValueError):
        raise HTTPException(status_code=503, detail="Video data is unavailable. Try again.") from None


@router.get("/subjects/{subject_id}/videos", response_model=SubjectVideosResponse)
def subject_videos(subject_id: UUID, user: CurrentUser) -> SubjectVideosResponse:
    try:
        if get_subject(subject_id) is None:
            raise HTTPException(status_code=404, detail="Subject not found.")
        videos = list_videos(user.id, subject_id=subject_id)
        return SubjectVideosResponse(videos=videos, summary=summarize(videos))
    except (SQLAlchemyError, ValueError):
        raise HTTPException(status_code=503, detail="Video data is unavailable. Try again.") from None


@router.patch("/videos/{video_id}/progress", response_model=VideoResponse)
def video_progress(video_id: UUID, body: ProgressUpdate, user: CurrentUser) -> VideoResponse:
    try:
        video = update_progress(video_id, user.id, body.status)
        if video is None:
            raise HTTPException(status_code=404, detail="Video not found.")
        return video
    except (SQLAlchemyError, ValueError):
        raise HTTPException(status_code=503, detail="Video status could not be saved. Try again.") from None
