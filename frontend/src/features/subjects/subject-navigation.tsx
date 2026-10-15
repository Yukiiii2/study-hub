import Link from "next/link";

export function SubjectNavigation({ subjectId, current }: { subjectId: string; current: "curriculum" | "lectures" }) {
  return <nav className="subject-sections view-tabs" aria-label="Subject sections">
    <Link href={`/subjects/${subjectId}`} aria-current={current === "curriculum" ? "page" : undefined}>Curriculum</Link>
    <Link href={`/subjects/${subjectId}/videos`} aria-current={current === "lectures" ? "page" : undefined}>Lectures</Link>
    <Link href={`/quizzes?${new URLSearchParams({ subject_id: subjectId })}`}>Practice</Link>
    <Link href={`/library?${new URLSearchParams({ subject_id: subjectId })}`}>Resources</Link>
  </nav>;
}
