import { QuizAttemptPage } from "@/features/quizzes/quiz-attempt";

export default async function AttemptPage({ params }: { params: Promise<{ attemptId: string }> }) {
  const { attemptId } = await params;
  return <QuizAttemptPage key={attemptId} attemptId={attemptId} />;
}
