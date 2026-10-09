"use client";

import { useState } from "react";
import type { ReviewQuestion } from "@/services/quizzes";
import { CardEditor } from "./card-editor";
import { cardFromMistake } from "./review-state";

export function MistakeFlashcardAction({ question }: { question: ReviewQuestion }) {
  const [editing, setEditing] = useState(false);
  const [saved, setSaved] = useState(false);
  return <div className="flashcard-mistake-action"><button type="button" className="secondary-button" onClick={() => { setSaved(false); setEditing(true); }}>Create flashcard</button>{saved && <p className="planner-notice" role="status">Flashcard saved. Review it in Flashcards or Recall.</p>}{editing && <CardEditor initial={cardFromMistake(question)} close={() => setEditing(false)} saved={() => setSaved(true)} />}</div>;
}
