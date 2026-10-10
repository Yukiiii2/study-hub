import type { SVGProps } from "react";

export type IconName = "dashboard" | "calendar" | "focus" | "subjects" | "library" | "quizzes" | "recall" | "flashcards" | "assessments" | "analytics" | "assistant" | "previous" | "next" | "plus" | "refresh" | "settings";

const paths: Record<IconName, string> = {
  dashboard: "M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z",
  calendar: "M5 5h14a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2z M3 10h18 M8 3v4 M16 3v4 M8 14h2 M14 14h2 M8 18h2",
  focus: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z M12 7v5l3 2",
  subjects: "M12 5v15 M3 4h4a7 7 0 0 1 5 2 7 7 0 0 1 5-2h4v15h-4a7 7 0 0 0-5 2 7 7 0 0 0-5-2H3z",
  library: "M4 4v16 M8 4v16 M12 4v16 M16 5l3-1 3 15-3 1z",
  quizzes: "M7 3h10v3H7z M7 5H5v16h14V5h-2 M8 11h8 M8 15h6",
  recall: "M4 10a8 8 0 1 1 1 8 M4 4v6h6 M12 8v5l3 2",
  flashcards: "M4 7h13v14H4z M8 3h13v14 M8 12h5 M8 16h3",
  assessments: "M12 3l9 4v6c0 4-5 7-9 9-4-2-9-5-9-9V7z M8 12l3 3 5-6",
  analytics: "M4 3v18h17 M8 16v-5 M13 16V7 M18 16v-8",
  assistant: "M4 4h16v12H9l-5 4z M8 9h8 M8 12h5",
  previous: "M15 6l-6 6 6 6",
  next: "M9 6l6 6-6 6",
  plus: "M12 5v14 M5 12h14",
  settings: "M4 7h16 M4 17h16 M8 4v6 M16 14v6",
  refresh: "M20 10a8 8 0 0 0-14-4L3 9 M3 4v5h5 M4 14a8 8 0 0 0 14 4l3-3 M21 20v-5h-5",
};

/** Consistent, decorative navigation geometry; the adjacent label names the action. */
export function InterfaceIcon({ name, ...props }: SVGProps<SVGSVGElement> & { name: IconName }) {
  return <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false" {...props}><path d={paths[name]} /></svg>;
}
