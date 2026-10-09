import type { Card, CardInput, CardReview, Rating, ReviewInput } from "@/services/flashcards";
import type { ReviewQuestion } from "@/services/quizzes";

export type PendingReview = { card: Card; body: ReviewInput };
export const ratingLabel = (rating: Rating) => ({ again: "Again", hard: "Hard", good: "Good", easy: "Easy" })[rating];
export function pendingReview(card: Card, rating: Rating, requestId: () => string = () => crypto.randomUUID()): PendingReview {
  return { card, body: { rating, expected_revision: card.review_revision, request_id: requestId() } };
}
export async function confirmReview(pending: PendingReview, submit: (id: string, body: ReviewInput) => Promise<CardReview>, accepted: (review: CardReview) => void) {
  const review = await submit(pending.card.id, pending.body);
  accepted(review);
}
export function cardIsDue(card: Card, asOf: string) {
  return card.status === "active" && new Date(card.next_review_at).getTime() <= new Date(asOf).getTime();
}
export function cardFromMistake(question: Pick<ReviewQuestion, "prompt" | "options" | "correct_keys" | "explanation" | "subject_id" | "topic_id" | "resource_id" | "source_page">): CardInput {
  const answer = question.options.filter((option) => question.correct_keys.includes(option.key)).map((option) => option.text).join("\n");
  return { front: question.prompt, back: `${answer}${question.explanation ? `\n\n${question.explanation}` : ""}`, notes: null, deck_id: null, subject_id: question.subject_id, topic_id: question.topic_id, resource_id: question.resource_id, source_page: question.source_page, status: "active" };
}
export function flashcardTimestamp(value: string, timezone: string) {
  return new Intl.DateTimeFormat("en", { timeZone: timezone, month: "short", day: "numeric", year: "numeric", hour: "numeric", minute: "2-digit" }).format(new Date(value));
}
