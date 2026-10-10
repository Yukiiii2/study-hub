import { AssistantPage, type AssistantInitial } from "@/features/assistant/assistant-page";

export default async function StudyAssistantPage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const query = await searchParams;
  const initial: AssistantInitial = {};
  for (const key of ["subject_id", "topic_id", "resource_id", "attempt_id", "question_id", "mode", "prompt"] as const) {
    const value = query[key]; if (typeof value === "string") initial[key] = value;
  }
  return <AssistantPage initial={initial} />;
}
