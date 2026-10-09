import type { Attempt, TakingQuestion } from "@/services/quizzes";

type DraftStorage = Pick<Storage, "getItem" | "setItem" | "removeItem">;
type Draft = { question_id: string; selected_keys: string[]; baseline_keys: string[] };
const storageKey = (attemptId: string) => `study-hub:quiz-draft:${attemptId}`;
const sameKeys = (first: string[], second: string[]) => [...first].sort().join("|") === [...second].sort().join("|");
function validKeys(value: unknown, question: TakingQuestion): value is string[] {
  return Array.isArray(value) && value.length <= (question.question_type === "multi_select" ? 6 : 1)
    && value.every((key) => typeof key === "string" && question.options.some((option) => option.key === key))
    && new Set(value).size === value.length;
}
function read(storage: DraftStorage | null, attemptId: string): Draft | null {
  try {
    const raw = storage?.getItem(storageKey(attemptId));
    if (!raw || raw.length > 2048) return null;
    const draft: unknown = JSON.parse(raw);
    if (!draft || typeof draft !== "object" || Array.isArray(draft)) return null;
    const candidate = draft as Draft;
    if (typeof candidate.question_id !== "string" || candidate.question_id.length > 100 || Object.keys(candidate).some((key) => !["question_id", "selected_keys", "baseline_keys"].includes(key))) return null;
    return candidate;
  } catch { return null; }
}
export function clearAttemptDraft(storage: DraftStorage | null, attemptId: string) {
  try { storage?.removeItem(storageKey(attemptId)); } catch { /* A denied storage API must not prevent server saves. */ }
}
export function rememberAttemptDraft(storage: DraftStorage | null, attempt: Attempt, question: TakingQuestion, selected: string[]) {
  if (attempt.status !== "in_progress" || !attempt.questions.some((item) => item.id === question.id) || !validKeys(selected, question)) return false;
  if (sameKeys(selected, question.selected_keys)) { clearAttemptDraft(storage, attempt.id); return true; }
  if (!storage) return false;
  const draft: Draft = { question_id: question.id, selected_keys: [...selected], baseline_keys: [...question.selected_keys] };
  try { storage.setItem(storageKey(attempt.id), JSON.stringify(draft)); return true; }
  catch { clearAttemptDraft(storage, attempt.id); return false; }
}
export function restoreAttemptDraft(storage: DraftStorage | null, attempt: Attempt): { index: number; question_id: string; selected_keys: string[] } | null {
  if (attempt.status !== "in_progress") { clearAttemptDraft(storage, attempt.id); return null; }
  const draft = read(storage, attempt.id);
  if (!draft) { clearAttemptDraft(storage, attempt.id); return null; }
  const index = attempt.questions.findIndex((question) => question.id === draft.question_id);
  const question = attempt.questions[index];
  if (!question || !validKeys(draft.selected_keys, question) || !validKeys(draft.baseline_keys, question)
    || !sameKeys(draft.baseline_keys, question.selected_keys) || sameKeys(draft.selected_keys, question.selected_keys)) {
    clearAttemptDraft(storage, attempt.id); return null;
  }
  return { index, question_id: question.id, selected_keys: [...draft.selected_keys] };
}
export function clearConfirmedDraft(storage: DraftStorage | null, attempt: Attempt) {
  if (attempt.status === "completed") { clearAttemptDraft(storage, attempt.id); return; }
  const draft = read(storage, attempt.id);
  if (!draft) return;
  const question = attempt.questions.find((item) => item.id === draft.question_id);
  if (question && validKeys(draft.selected_keys, question) && sameKeys(question.selected_keys, draft.selected_keys)) clearAttemptDraft(storage, attempt.id);
}
export function browserDraftStorage(): DraftStorage | null {
  try { return window.sessionStorage; } catch { return null; }
}
