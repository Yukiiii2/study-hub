import { ApiError, authenticatedDelete, authenticatedGet, authenticatedPatch, authenticatedPost } from "./api";

export const eventTypes = ["lecture", "reading", "drill", "recall", "quiz", "assessment", "general"] as const;
export type EventType = typeof eventTypes[number];
export type EventStatus = "scheduled" | "completed" | "skipped" | "cancelled";
export type EventCreate = { subject_id: string | null; topic_id: string | null; title: string; event_type: EventType; start_at: string; end_at: string; timezone: string; status: EventStatus; recurrence_rule: string | null; notes: string | null };
export type StudyEvent = EventCreate & { id: string; created_at: string; updated_at: string; occurrence_date?: string | null; is_recurring?: boolean; occurrence_id?: string | null };
export type TaskInput = { subject_id: string | null; topic_id: string | null; title: string; task_type: EventType; estimated_minutes: number | null; due_at: string | null; status: "pending" | "completed" | "cancelled" };
export type StudyTask = Omit<TaskInput, "status"> & { id: string; status: TaskInput["status"] | "scheduled"; scheduled_event_id: string | null; created_at: string; updated_at: string };
export const activityTypes = ["lecture", "reading", "practice", "recall", "quiz", "general"] as const;
export type ActivityType = typeof activityTypes[number];
export type StudySession = { id: string; study_event_id: string | null; occurrence_id: string | null; subject_id: string | null; topic_id: string | null; activity_type: ActivityType; started_at: string; ended_at: string | null; duration_seconds: number | null; notes: string | null; created_at: string };
export type PlannerContext = { timezone: string; active_session: StudySession | null };
const base = "/api/study-events";
const eventPath = (event: StudyEvent, series = false) => `${base}/${encodeURIComponent(event.id)}${!series && event.occurrence_date ? `/occurrences/${event.occurrence_date}` : ""}`;
export const getPlannerContext = (signal?: AbortSignal) => authenticatedGet<PlannerContext>("/api/study-plan/context", signal);
export const getEvents = (start: string, end: string, signal?: AbortSignal) => authenticatedGet<StudyEvent[]>(`${base}?${new URLSearchParams({ start_at: start, end_at: end })}`, signal);
export const getEvent = (id: string, signal?: AbortSignal) => authenticatedGet<StudyEvent>(`${base}/${encodeURIComponent(id)}`, signal);
export const createEvent = (body: EventCreate) => authenticatedPost<StudyEvent>(base, body);
export const updateEvent = (event: StudyEvent, body: Partial<EventCreate>, series = false) => authenticatedPatch<StudyEvent>(eventPath(event, series), body);
export const deleteEvent = (event: StudyEvent, series = false) => authenticatedDelete(eventPath(event, series));
export const getTasks = (signal?: AbortSignal) => authenticatedGet<StudyTask[]>("/api/study-tasks", signal);
export const createTask = (body: TaskInput) => authenticatedPost<StudyTask>("/api/study-tasks", body);
export const updateTask = (id: string, body: Partial<TaskInput>) => authenticatedPatch<StudyTask>(`/api/study-tasks/${encodeURIComponent(id)}`, body);
export const deleteTask = (id: string) => authenticatedDelete(`/api/study-tasks/${encodeURIComponent(id)}`);
export const scheduleTask = (id: string, body: EventCreate) => authenticatedPost<StudyEvent>(`/api/study-tasks/${encodeURIComponent(id)}/schedule`, body);
export function eventActivity(event: StudyEvent): ActivityType {
  return event.event_type === "drill" ? "practice" : event.event_type === "assessment" ? "general" : event.event_type;
}
export const startSession = (event?: StudyEvent) => authenticatedPost<StudySession>("/api/study-sessions", event ? { study_event_id: event.id, activity_type: eventActivity(event), ...(event.occurrence_date ? { occurrence_date: event.occurrence_date } : {}) } : {});
export const stopSession = (id: string) => authenticatedPatch<StudySession>(`/api/study-sessions/${encodeURIComponent(id)}`, { action: "stop" });
export function plannerError(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 422) return "Check the dates, recurrence weekdays and subject/topic selection. The request was not saved.";
    if (error.status === 409) return "This change conflicts with the saved plan. A task may already be scheduled, a session may be active, or recurrence changes may conflict with saved occurrences. Refresh and review the current state.";
    if (error.status === 404) return "This item is no longer available. Refresh the planner.";
    return error.message;
  }
  return error instanceof Error ? error.message : "Could not update the planner. Try again.";
}
