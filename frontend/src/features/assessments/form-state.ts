import { localToInstant, zonedParts } from "@/features/study-plan/dates";
import type { AssessmentAttemptInput } from "@/services/assessments";

export function assessmentLocal(instant: string | null | undefined, timezone: string): string {
  if (!instant) return "";
  const parts = zonedParts(instant, timezone); return `${parts.date}T${parts.time}`;
}
export function assessmentInstant(local: string, timezone: string): string | null { return local ? localToInstant(local.slice(0, 10), local.slice(11), timezone) : null; }
export function assessmentEditedInstant(local: string, timezone: string, original?: string | null): string | null {
  return original && local === assessmentLocal(original, timezone) ? original : assessmentInstant(local, timezone);
}
export function assessmentTimestamp(instant: string, timezone: string): string { return new Intl.DateTimeFormat("en", { timeZone: timezone, month: "short", day: "numeric", year: "numeric", hour: "numeric", minute: "2-digit" }).format(new Date(instant)); }
export function wholeSubjectCoverage(selected: string[], subject: string, topics: { id: string; subject_id: string }[]): string[] { const removed = new Set(topics.filter((topic) => topic.subject_id === subject).map((topic) => topic.id)); return selected.filter((id) => !removed.has(id)); }
export type AttemptFields = { started: string; completed: string; score: string; maximum: string; notes: string };
export function attemptInput(fields: AttemptFields, timezone: string, original?: Pick<AssessmentAttemptInput, "started_at" | "completed_at">): AssessmentAttemptInput {
  const hasScore = fields.score.trim() !== "", hasMax = fields.maximum.trim() !== "";
  if (hasScore !== hasMax) throw new Error("Enter both a score and maximum score, or leave both blank for an unscored result.");
  const score = hasScore ? Number(fields.score) : null, max = hasMax ? Number(fields.maximum) : null;
  if (score !== null && max !== null && (!Number.isFinite(score) || !Number.isFinite(max) || score < 0 || max <= 0 || score > max)) throw new Error("Use a finite nonnegative score no greater than a positive maximum score.");
  const started_at = assessmentEditedInstant(fields.started, timezone, original?.started_at), completed_at = assessmentEditedInstant(fields.completed, timezone, original?.completed_at);
  if (score !== null && !completed_at) throw new Error("Enter a completion date and time for a scored result.");
  if (started_at && completed_at && Date.parse(completed_at) < Date.parse(started_at)) throw new Error("Completion cannot be before the start time.");
  return { started_at, completed_at, score, max_score: max, notes: fields.notes.trim() || null };
}
