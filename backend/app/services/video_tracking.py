from app.schemas.videos import VideoResponse, VideoSummary


def summarize(videos: list[VideoResponse]) -> VideoSummary:
    total = sum(v.duration_seconds for v in videos if v.duration_seconds is not None)
    completed = sum(v.duration_seconds for v in videos if v.status == "completed" and v.duration_seconds is not None)
    return VideoSummary(total_videos=len(videos), completed_videos=sum(v.status == "completed" for v in videos),
                        total_duration_seconds=total, completed_duration_seconds=completed,
                        remaining_duration_seconds=total-completed,
                        unknown_duration_videos=sum(v.duration_seconds is None for v in videos))
