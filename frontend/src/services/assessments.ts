import { ApiError, authenticatedDelete, authenticatedGet, authenticatedPatch, authenticatedPost } from "./api";

export type AssessmentStatus = "planned" | "completed" | "cancelled" | "archived";
export type AssessmentInput = { title: string; description: string | null; scheduled_at: string | null; status: AssessmentStatus; topic_ids: string[]; subject_ids: string[] };
export type CoverageTopic = { id: string; subject_id: string; code: string | null; title: string };
export type CoverageSubject = { id: string; code: string; name: string; scope: "all_topics" | "selected_topics" };
export type Assessment = AssessmentInput & { id: string; created_at: string; updated_at: string; coverage_topics: CoverageTopic[]; coverage_subjects: CoverageSubject[]; topic_count: number };
export type Readiness = { topic_count: number; total_videos: number; completed_videos: number; video_completion_percentage: number | null; quiz_graded_answers: number; quiz_correct_answers: number; quiz_accuracy_percentage: number | null; active_flashcards: number; reviewed_flashcards: number; due_flashcards: number; overdue_flashcards: number; as_of: string; timezone: string };
export type AssessmentDetail = Assessment & { readiness: Readiness };
export type AssessmentAttemptInput = { started_at: string | null; completed_at: string | null; score: number | null; max_score: number | null; notes: string | null };
export type AssessmentAttempt = AssessmentAttemptInput & { id: string; assessment_id: string; percentage: number | null; created_at: string; updated_at: string };
export type AssessmentFilters = { status?: AssessmentStatus | "all"; q?: string; limit?: number; offset?: number };
function query(filters: AssessmentFilters | { limit?: number; offset?: number }) { const params = new URLSearchParams(); for (const [key, value] of Object.entries(filters)) if (value !== undefined && value !== "") params.set(key, String(value)); return `?${params}`; }
const assessmentPath = (id: string) => `/api/assessments/${encodeURIComponent(id)}`;
export const getAssessments = (filters: AssessmentFilters, signal?: AbortSignal) => authenticatedGet<{ assessments: Assessment[]; total: number }>(`/api/assessments${query(filters)}`, signal);
export const getAssessment = (id: string, signal?: AbortSignal) => authenticatedGet<AssessmentDetail>(assessmentPath(id), signal);
export const createAssessment = (body: AssessmentInput) => authenticatedPost<Assessment>("/api/assessments", body);
export const updateAssessment = (id: string, body: Partial<AssessmentInput>) => authenticatedPatch<Assessment>(assessmentPath(id), body);
export const archiveAssessment = (id: string) => authenticatedDelete(assessmentPath(id));
export const getAssessmentAttempts = (id: string, filters: { limit?: number; offset?: number } = {}, signal?: AbortSignal) => authenticatedGet<{ attempts: AssessmentAttempt[]; total: number }>(`${assessmentPath(id)}/attempts${query(filters)}`, signal);
export const createAttempt = (id: string, body: AssessmentAttemptInput) => authenticatedPost<AssessmentAttempt>(`${assessmentPath(id)}/attempts`, body);
export const updateAttempt = (id: string, body: AssessmentAttemptInput) => authenticatedPatch<AssessmentAttempt>(`/api/assessment-attempts/${encodeURIComponent(id)}`, body);
export function assessmentError(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 422) return "Check the required title, coverage and dates. Results need both score values and a completion time when scored.";
    if (error.status === 409) return "This assessment is archived or its saved state has changed. Refresh before trying again.";
    if (error.status === 404) return "This assessment or result is no longer available. Return to assessments and refresh.";
    return error.message;
  }
  return error instanceof Error ? error.message : "The assessment request failed. Try again.";
}
