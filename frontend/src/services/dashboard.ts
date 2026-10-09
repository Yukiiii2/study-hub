import { authenticatedGet } from "./api";
import type { Subject } from "./subjects";
import type { StudyEvent, StudyTask } from "./study-plan";
import type { SubjectVideos } from "./videos";

type CurriculumContext = { subject_code: string | null; topic_title: string | null };
export type DashboardData = {
  date: string;
  timezone: string;
  generated_at: string;
  today_events: (StudyEvent & CurriculumContext)[];
  upcoming_tasks: (StudyTask & CurriculumContext)[];
  video_summary: SubjectVideos["summary"] & { remaining_videos: number };
  recall_summary: { overdue: number; due_today: number };
  subjects: (Subject & { topic_count: number; video_count: number; completed_video_count: number })[];
  continue_video_subject_id: string | null;
};

export const getDashboard = (signal?: AbortSignal) => authenticatedGet<DashboardData>("/api/dashboard", signal);
