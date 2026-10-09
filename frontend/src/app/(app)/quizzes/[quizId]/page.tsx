import { QuizDetailPage } from "@/features/quizzes/quiz-builder";

export default async function QuizPage({ params }: { params: Promise<{ quizId: string }> }) {
  const { quizId } = await params;
  return <QuizDetailPage key={quizId} quizId={quizId} />;
}
