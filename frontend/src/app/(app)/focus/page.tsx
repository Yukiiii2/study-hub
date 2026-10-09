import { FocusPage } from "@/features/focus/focus-page";

export default async function Page({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const values = await searchParams;
  const value = (key: string) => typeof values[key] === "string" ? values[key] as string : "";
  return <FocusPage subjectId={value("subject_id")} topicId={value("topic_id")} eventId={value("study_event_id")} occurrenceDate={value("occurrence_date")} />;
}
