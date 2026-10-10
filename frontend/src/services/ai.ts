import { ApiError, authenticatedPost } from "./api";
import type { QuestionInput } from "./quizzes";
import type { CardInput } from "./flashcards";

export type AIContext = { subject_id?: string | null; topic_id?: string | null; resource_id?: string | null };
export type AICitation = { resource_id: string; resource_title: string; page_number: number; quote: string };
export type AIResponse = { provider: string | null; model: string | null; generated_at: string; context: AIContext; grounding: "resource" | "topic_context" | "quiz_snapshot" | "none"; insufficient_context: boolean; notice: string | null; citations: AICitation[] };
export type AIAnswer = AIResponse & { answer: string };
export type AIQuestionDraft = QuestionInput & { ai_draft_receipt: string };
export type AICardDraft = CardInput & { ai_draft_receipt: string };
export type AIQuestions = AIResponse & { questions: AIQuestionDraft[] };
export type AICards = AIResponse & { cards: AICardDraft[] };
export type AIResult = AIAnswer | AIQuestions | AICards;
export type AIMode = "ask" | "quiz" | "cards";
export type AIDifficulty = "basic" | "intermediate" | "advanced";
export type SnapshotContext = { attempt_id: string; question_id: string };
export const askAI = (body: AIContext & { prompt: string }, signal?: AbortSignal) => authenticatedPost<AIAnswer>("/api/ai/ask", body, signal);
export const generateAIQuestions = (body: AIContext & { prompt?: string; count: number; difficulty: AIDifficulty }, signal?: AbortSignal) => authenticatedPost<AIQuestions>("/api/ai/generate-quiz", body, signal);
export const generateAICards = (body: AIContext & Partial<SnapshotContext> & { prompt?: string; count: number }, signal?: AbortSignal) => authenticatedPost<AICards>("/api/ai/generate-flashcards", body, signal);
export const explainAIAnswer = (body: SnapshotContext, signal?: AbortSignal) => authenticatedPost<AIAnswer>("/api/ai/explain-answer", body, signal);
export function aiError(error: unknown) {
  if (error instanceof ApiError) {
    if (error.status === 429 || error.status === 409) return "AI assistance is busy or its request limit was reached. Wait before trying again.";
    if (error.status === 404) return "This source or completed quiz answer is no longer available. Choose another context.";
    if (error.status === 422 || error.status === 413) return "Check the context, prompt length and requested number of drafts.";
    if (error.status === 503) return "AI assistance is unavailable or has not been configured. Try again later.";
    if (error.status === 502 || error.status === 504) return "AI assistance could not return a verified response. Try again later.";
    if (error.status === 401) return error.message;
  }
  return "AI assistance could not complete this request. Try again. Your existing preview is retained.";
}
