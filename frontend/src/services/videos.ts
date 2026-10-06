import { authenticatedGet, authenticatedPatch } from "./api";

export type VideoStatus = "not_started" | "in_progress" | "completed";
export type Video = {
  id: string;
  topic_id: string;
  topic_code: string | null;
  topic_title: string;
  title: string;
  duration_seconds: number | null;
  display_order: number;
  status: VideoStatus;
  watched_seconds: number | null;
  completed_at: string | null;
};
export type SubjectVideos = {
  videos: Video[];
  summary: {
    total_videos: number;
    completed_videos: number;
    total_duration_seconds: number;
    completed_duration_seconds: number;
    remaining_duration_seconds: number;
    unknown_duration_videos: number;
  };
};

export function getSubjectVideos(subjectId: string, signal?: AbortSignal) {
  return authenticatedGet<SubjectVideos>(`/api/subjects/${encodeURIComponent(subjectId)}/videos`, signal);
}

export function setVideoProgress(videoId: string, status: VideoStatus, signal?: AbortSignal) {
  return authenticatedPatch<Video>(`/api/videos/${encodeURIComponent(videoId)}/progress`, { status }, signal);
}
