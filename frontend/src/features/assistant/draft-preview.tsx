"use client";

import Link from "next/link";
import { SectionHeader } from "@/components/study-ui";
import { useState } from "react";
import type { AICards, AIQuestions } from "@/services/ai";
import { QuestionEditor } from "@/features/quizzes/question-editor";
import { CardEditor } from "@/features/flashcards/card-editor";
import { AIResponseView } from "./response-view";

export function AIDraftPreview({ response, disabled = false }: { response: AIQuestions | AICards; disabled?: boolean }) {
  const [removed, setRemoved] = useState<number[]>([]);
  const [savedIds, setSavedIds] = useState<Record<number, string>>({});
  const [uncertainIds, setUncertainIds] = useState<number[]>([]);
  const [editing, setEditing] = useState<number | null>(null);
  const questions = "questions" in response ? response.questions : null;
  const cards = "cards" in response ? response.cards : null;
  const drafts = questions ?? cards ?? [];
  const visible = drafts.map((_, index) => index).filter((index) => !removed.includes(index));
  return <section className="assistant-preview" aria-labelledby="ai-preview-heading"><SectionHeader title={`Review ${questions ? "question" : "flashcard"} drafts`} titleId="ai-preview-heading" /><p className="resource-note">Nothing is saved automatically. Review and edit each draft, then confirm its save. Removed drafts are discarded.{cards ? " Saved AI cards stay suspended until you activate them in Flashcards." : " Saved questions appear in Question Bank; create a quiz there when ready."}</p>
    <AIResponseView response={response} />
    {!visible.length && <p className="resource-note" role="status">All drafts were removed. Generate another preview when ready.</p>}
    <ol className="assistant-drafts">{visible.map((index) => <li key={index}><h3>{questions ? questions[index].prompt : cards![index].front}</h3>{questions ? <><ul>{questions[index].options.map((option) => <li key={option.key}>{option.key}: {option.text}{questions[index].correct_keys.includes(option.key) ? " (correct)" : ""}</li>)}</ul>{questions[index].explanation && <p className="assistant-answer">{questions[index].explanation}</p>}</> : <p className="assistant-answer">{cards![index].back}</p>}
      {drafts[index].resource_id && <p className="resource-note"><Link className="quiz-text-link" href={`/library/${encodeURIComponent(drafts[index].resource_id!)}`}>Open source{drafts[index].source_page ? ` · Page ${drafts[index].source_page}` : ""}</Link></p>}
      <div className="resource-actions">{savedIds[index] ? <p className="planner-notice" role="status">Saved. <Link className="quiz-text-link" href={questions ? "/question-bank" : "/flashcards"}>Open {questions ? "Question Bank" : "Flashcards"}</Link></p> : uncertainIds.includes(index) ? <p className="auth-error" role="alert">This card may already be saved. <Link className="quiz-text-link" href="/flashcards">Check Flashcards</Link> before creating another draft.</p> : <><button type="button" className="secondary-button" disabled={disabled} onClick={() => setEditing(index)}>Review, edit and save</button><button type="button" className="secondary-button" disabled={disabled} onClick={() => setRemoved((current) => [...current, index])}>Remove draft</button></>}</div>
    </li>)}</ol>
    {editing !== null && !savedIds[editing] && (questions ? <QuestionEditor initial={questions[editing]} close={() => setEditing(null)} saved={(question) => setSavedIds((current) => ({ ...current, [editing]: question.id }))} /> : <CardEditor initial={cards![editing]} close={() => setEditing(null)} saved={(card) => setSavedIds((current) => ({ ...current, [editing]: card.id }))} uncertain={() => setUncertainIds((current) => [...current, editing])} />)}
  </section>;
}
