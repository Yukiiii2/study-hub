import { ApiError, authenticatedGet, authenticatedPatch, authenticatedPost } from "./api";
import type { AIProvenance } from "./ai-provenance";

export type QuestionType = "single_select" | "multi_select" | "true_false";
export type QuestionOption = { key: string; text: string };
export type QuestionInput = { subject_id: string | null; topic_id: string | null; resource_id: string | null; source_page: number | null; question_type: QuestionType; prompt: string; explanation: string | null; options: QuestionOption[]; correct_keys: string[]; ai_draft_receipt?: string };
export type Question = Omit<QuestionInput, "ai_draft_receipt"> & { id: string; origin: "manual" | "csv" | "ai"; ai_provenance?: AIProvenance | null; is_archived: boolean; created_at: string; updated_at: string };
export type TakingQuestion = Omit<QuestionInput, "correct_keys" | "explanation"> & { id: string; selected_keys: string[] };
export type ReviewQuestion = TakingQuestion & { correct_keys: string[]; explanation: string | null; is_correct: boolean };
export type QuizInput = { title: string; description: string | null; subject_id: string | null; topic_id: string | null; question_ids: string[] };
export type Quiz = Omit<QuizInput, "question_ids"> & { id: string; is_archived: boolean; question_count: number; active_attempt_id: string | null; created_at: string; updated_at: string };
export type QuizDetail = Quiz & { questions: Omit<TakingQuestion, "selected_keys">[] };
export type AttemptSummary = { id: string; quiz_id: string; title: string; status: "in_progress" | "completed"; started_at: string; completed_at: string | null; score_value: number | null; total_questions: number; score_percent: number | null };
export type Attempt = AttemptSummary & { questions: (TakingQuestion | ReviewQuestion)[] };
export type QuestionList = { questions: Question[]; total: number };
export type QuizList = { quizzes: Quiz[]; total: number };
export type AttemptList = { attempts: AttemptSummary[]; total: number };
export type Issue = { row: number; field: string; message: string };
export type ImportPreview = { row_count: number; valid_count: number; duplicate_count: number; proposed_inserts: number; unchanged: number; warnings: Issue[]; errors: Issue[]; sample: QuestionInput[]; preview_token: string | null };
export type Filters = { limit?: number; offset?: number; q?: string; subject_id?: string; topic_id?: string; resource_id?: string; question_type?: string; quiz_id?: string };
function query(filters: Filters) { const params = new URLSearchParams(); for (const [key, value] of Object.entries(filters)) if (value !== undefined && value !== "") params.set(key, String(value)); return `?${params}`; }
const questionPath = (id: string) => `/api/questions/${encodeURIComponent(id)}`;
const quizPath = (id: string) => `/api/quizzes/${encodeURIComponent(id)}`;
const attemptPath = (id: string) => `/api/quiz-attempts/${encodeURIComponent(id)}`;
export const getQuestions = (filters: Filters, signal?: AbortSignal) => authenticatedGet<QuestionList>(`/api/questions${query(filters)}`, signal);
export const getQuestion = (id: string, signal?: AbortSignal) => authenticatedGet<Question>(questionPath(id), signal);
export const createQuestion = (body: QuestionInput) => authenticatedPost<Question>("/api/questions", body);
export const updateQuestion = (id: string, body: QuestionInput) => authenticatedPatch<Question>(questionPath(id), body);
export const archiveQuestion = (id: string) => authenticatedPatch<Question>(questionPath(id), { is_archived: true });
export const getQuizzes = (filters: Filters, signal?: AbortSignal) => authenticatedGet<QuizList>(`/api/quizzes${query(filters)}`, signal);
export const getQuiz = (id: string, signal?: AbortSignal) => authenticatedGet<QuizDetail>(quizPath(id), signal);
export const createQuiz = (body: QuizInput) => authenticatedPost<QuizDetail>("/api/quizzes", body);
export const updateQuiz = (id: string, body: QuizInput) => authenticatedPatch<QuizDetail>(quizPath(id), body);
export const archiveQuiz = (id: string) => authenticatedPatch<QuizDetail>(quizPath(id), { is_archived: true });
export const startAttempt = (id: string) => authenticatedPost<Attempt>(`${quizPath(id)}/attempts`, undefined);
export const getAttempts = (filters: Filters, signal?: AbortSignal) => authenticatedGet<AttemptList>(`/api/quiz-attempts${query(filters)}`, signal);
export const getAttempt = (id: string, signal?: AbortSignal) => authenticatedGet<Attempt>(attemptPath(id), signal);
export const saveAnswer = (id: string, questionId: string, selectedKeys: string[]) => authenticatedPost<Attempt>(`${attemptPath(id)}/answers`, { question_id: questionId, selected_keys: selectedKeys });
export const completeAttempt = (id: string) => authenticatedPost<Attempt>(`${attemptPath(id)}/complete`, undefined);
export const getResults = (id: string, signal?: AbortSignal) => authenticatedGet<Attempt>(`${attemptPath(id)}/results`, signal);
export function previewQuestions(file: File) { const body = new FormData(); body.append("file", file); return authenticatedPost<ImportPreview>("/api/imports/questions/preview", body); }
export function commitQuestions(file: File, token: string) { const body = new FormData(); body.append("file", file); body.append("preview_token", token); return authenticatedPost<{ inserted: number; unchanged: number }>("/api/imports/questions/commit", body); }
export function quizError(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 404) return "This quiz or question is no longer available. Refresh and try again.";
    if (error.status === 409) return "This action conflicts with the saved state. Refresh before trying again.";
    if (error.status === 422) return "Check the required fields, answer choices and subject/topic/source associations. For CSV, preview the file again.";
    if (error.status === 413) return "Choose a CSV file no larger than 1 MiB.";
    return error.message;
  }
  return "The quiz request failed. Try again.";
}
export function questionCsvError(file: Pick<File, "name" | "size">) {
  if (!/\.csv$/i.test(file.name)) return "Choose a CSV file.";
  if (!file.size) return "This file is empty.";
  return file.size > 1_048_576 ? "Choose a CSV file no larger than 1 MiB." : null;
}
