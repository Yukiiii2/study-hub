import { validContextId } from "./draft-state";
import type { AIContext } from "@/services/ai";

/** Labels are local UI hints. Only explicit, supported source IDs enter API bodies. */
export function assistantPageContext(pathname: string) {
  const [area = "", id = ""] = pathname.split("/").filter(Boolean);
  const labels: Record<string, string> = { "": "Today", "study-plan": "Study Plan", focus: "Focus", subjects: "Subjects", library: "Library", recall: "Recall", flashcards: "Flashcards", quizzes: "Quizzes", "question-bank": "Question Bank", assessments: "Assessments", analytics: "Analytics", settings: "Settings", assistant: "Assistant" };
  const source: AIContext = {};
  if (area === "subjects" && validContextId(id)) source.subject_id = id;
  if (area === "library" && validContextId(id)) source.resource_id = id;
  const prompts: Record<string, string[]> = {
    "": ["Help me choose what to study next", "Help me organize my study day"],
    "study-plan": ["Help me build a study plan", "How can I balance my subjects?"],
    subjects: ["Explain a topic I am studying", "What should I study next in this subject?"],
    library: ["Summarize the selected resource", "Help me understand my notes"],
    recall: ["Help me understand a recall concept", "Give me a memory aid"],
    quizzes: ["Help me review a quiz mistake", "Explain a practice concept"],
    assessments: ["Help me prepare for an assessment", "Help me review my coverage"],
    analytics: ["How can I reflect on my study habits?", "How can I improve my study routine?"],
  };
  return { label: labels[area] ?? "Study workspace", source, prompts: prompts[area] ?? ["Explain a study concept", "Help me review this material"] };
}
