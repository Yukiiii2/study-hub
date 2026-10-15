import { QuizListPage } from "@/features/quizzes/quiz-list";

export default async function QuizzesPage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) { const params = await searchParams; return <QuizListPage key={typeof params.subject_id === "string" ? params.subject_id : ""} initialSubject={typeof params.subject_id === "string" ? params.subject_id : ""} />; }
