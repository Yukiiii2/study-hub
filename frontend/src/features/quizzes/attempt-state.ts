import type { Attempt, ReviewQuestion, TakingQuestion } from "@/services/quizzes";

export function reviewQuestion(attempt: Attempt, question: TakingQuestion | ReviewQuestion): ReviewQuestion | null {
  return attempt.status === "completed" && "correct_keys" in question && "is_correct" in question ? question : null;
}
// Navigation receives only the server-confirmed attempt; rejection leaves the draft in place.
export async function persistBeforeAction(save: () => Promise<Attempt>, accept: (attempt: Attempt) => void, action: (attempt: Attempt) => void | Promise<void>) {
  const attempt = await save();
  accept(attempt);
  await action(attempt);
}
