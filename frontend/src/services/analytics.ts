import { ApiError, authenticatedGet, authenticatedPost } from "./api";
import type { ActivityType, StudySession } from "./study-plan";

export type LabeledSession = StudySession & { subject_code: string | null; subject_title: string | null; topic_title: string | null };
export type FocusData = { timezone: string; server_now: string; active_session: StudySession | null; today_seconds: number; today_session_count: number; recent_sessions: LabeledSession[] };
export type AnalyticsRange = { period: 7 | 30 | 90 } | { start_date: string; end_date: string };
export type DailyActivity = { date: string; duration_seconds: number; session_count: number };
export type AnalyticsData = {
  timezone: string; start_date: string; end_date: string;
  summary: { total_seconds: number; session_count: number; active_days: number; average_session_seconds: number; longest_session_seconds: number; planned_seconds: number };
  daily: DailyActivity[];
  subjects: { subject_id: string | null; subject_code: string | null; subject_title: string | null; subject_color_key: string | null; duration_seconds: number; session_count: number; planned_seconds: number }[];
  activities: { activity_type: ActivityType; duration_seconds: number; session_count: number }[];
};
export type SessionHistory = { sessions: LabeledSession[]; total: number; limit: number; offset: number };
export type FocusStart = { study_event_id?: string; occurrence_date?: string; subject_id?: string; topic_id?: string; activity_type: ActivityType };
const query = (range: AnalyticsRange) => new URLSearchParams(Object.entries(range).map(([key, value]) => [key, String(value)]));
export const getFocus = (signal?: AbortSignal) => authenticatedGet<FocusData>("/api/focus", signal);
export const startFocus = (body: FocusStart) => authenticatedPost<StudySession>("/api/study-sessions", body);
export const getAnalytics = (range: AnalyticsRange, signal?: AbortSignal) => authenticatedGet<AnalyticsData>(`/api/analytics/summary?${query(range)}`, signal);
export const getAnalyticsSessions = (range: AnalyticsRange, offset: number, signal?: AbortSignal) => authenticatedGet<SessionHistory>(`/api/analytics/sessions?${query(range)}&limit=20&offset=${offset}`, signal);
export function studyTimeError(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 409) return "A session is already active. Refresh to restore it before starting another.";
    if (error.status === 422) return "Check your subject, topic, planned event and date selection. The request was not saved.";
    if (error.status === 404) return "This study item is no longer available. Refresh and choose another.";
    return error.message;
  }
  return "Could not load or save study time. Try again.";
}
