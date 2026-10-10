"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { completeAttempt, getAttempt, quizError, saveAnswer, type Attempt, type TakingQuestion, type ReviewQuestion } from "@/services/quizzes";
import { persistBeforeAction, reviewQuestion } from "./attempt-state";
import { browserDraftStorage, clearAttemptDraft, clearConfirmedDraft, rememberAttemptDraft, restoreAttemptDraft } from "./draft-recovery";
import { LoadNotice, QuizDialog, useQuizLoad } from "./shared";
import { ExplainAnswerAction } from "@/features/assistant/explain-answer";
import { MistakeFlashcardAction } from "@/features/flashcards/mistake-flashcard";

export function AttemptQuestionView({ attempt, question, selected, change, busy, openSource }: { attempt: Attempt; question: TakingQuestion | ReviewQuestion; selected: string[]; change: (keys: string[]) => void; busy: boolean; openSource?: (id: string) => void }) {
  const review = reviewQuestion(attempt, question);
  const completed = attempt.status === "completed";
  return <section className="quiz-question" aria-labelledby="taking-question-title"><h2 id="taking-question-title">{question.prompt}</h2><p className="resource-note">{question.question_type === "multi_select" ? "Select all answers that apply." : "Select one answer."} You may leave this question unanswered.</p><fieldset className="quiz-answer-options" disabled={busy || completed}><legend className="quiz-sr-only">Your answer</legend>{question.options.map((option) => <label className="quiz-answer" key={option.key} data-selected={selected.includes(option.key)}><input type={question.question_type === "multi_select" ? "checkbox" : "radio"} name={`answer-${question.id}`} checked={selected.includes(option.key)} onChange={(event) => change(question.question_type === "multi_select" ? event.target.checked ? [...selected, option.key] : selected.filter((key) => key !== option.key) : [option.key])} /><span className="quiz-answer-key">{option.key}</span><span>{option.text}</span></label>)}{!completed && <button type="button" className="secondary-button" disabled={busy || !selected.length} onClick={() => change([])}>Clear answer</button>}</fieldset>
    {review && <section className="quiz-review" aria-label="Answer review"><p className="quiz-review-result">{review.is_correct ? "Correct" : "Incorrect"}{!question.selected_keys.length ? " · Unanswered" : ""}</p><p>Your answer: {question.selected_keys.join(", ") || "No answer"}</p><p>Correct answer: {review.correct_keys.join(", ")}</p>{review.explanation && <><h3>Explanation</h3><p className="quiz-explanation">{review.explanation}</p></>}<ExplainAnswerAction key={`${attempt.id}:${question.id}`} attemptId={attempt.id} questionId={question.id} />{!review.is_correct && <><MistakeFlashcardAction key={question.id} question={review} /><Link className="topic-focus-link" href={`/assistant?${new URLSearchParams({ mode: "cards", attempt_id: attempt.id, question_id: question.id })}`}>Create AI flashcard drafts from this mistake</Link></>}</section>}
    {question.resource_id && <p className="resource-note">Source: <Link className="quiz-text-link" href={`/library/${question.resource_id}`} onClick={openSource ? (event) => { event.preventDefault(); if (!busy) openSource(question.resource_id!); } : undefined}>Open resource{question.source_page ? ` · Page ${question.source_page}` : ""}</Link></p>}
  </section>;
}
export function QuizAttemptPage({ attemptId }: { attemptId: string }) {
  const router = useRouter();
  const loaded = useQuizLoad(useCallback((signal) => getAttempt(attemptId, signal), [attemptId]));
  const [index, setIndex] = useState(0);
  const [draft, setDraft] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [writeError, setWriteError] = useState<string | null>(null);
  const [confirm, setConfirm] = useState(false);
  const [restored, setRestored] = useState(false);
  const [recoveryUnavailable, setRecoveryUnavailable] = useState(false);
  const hydrated = useRef(false);
  const pendingRestore = useRef<{ question_id: string; selected_keys: string[] } | null>(null);
  const attempt = loaded.data;
  const question = attempt?.questions[index];
  const completed = attempt?.status === "completed";
  const dirty = !!question && !completed && [...draft].sort().join("|") !== [...question.selected_keys].sort().join("|");
  useEffect(() => {
    if (!attempt || !question) return;
    if (attempt.status === "completed") clearAttemptDraft(browserDraftStorage(), attempt.id);
    if (!hydrated.current) {
      hydrated.current = true;
      const recovery = restoreAttemptDraft(browserDraftStorage(), attempt);
      if (recovery) {
        if (recovery.index !== index) pendingRestore.current = recovery;
        setIndex(recovery.index); setDraft(recovery.selected_keys); setRestored(true); return;
      }
    }
    if (pendingRestore.current?.question_id === question.id) {
      setDraft(pendingRestore.current.selected_keys); pendingRestore.current = null; return;
    }
    setDraft([...question.selected_keys]);
  }, [attempt, question, index]);
  useEffect(() => {
    if (!dirty) return;
    const warn = (event: BeforeUnloadEvent) => { event.preventDefault(); event.returnValue = ""; };
    window.addEventListener("beforeunload", warn); return () => window.removeEventListener("beforeunload", warn);
  }, [dirty]);
  async function persist(): Promise<Attempt> {
    if (!attempt || !question) throw new Error("Attempt unavailable.");
    return dirty ? saveAnswer(attempt.id, question.id, draft) : attempt;
  }
  async function action(next: (saved: Attempt) => void | Promise<void>) {
    if (busy) return;
    setBusy(true); setWriteError(null);
    try { await persistBeforeAction(persist, (saved) => { clearConfirmedDraft(browserDraftStorage(), saved); loaded.setData(saved); setRestored(false); setRecoveryUnavailable(false); }, next); }
    catch (failure) { setWriteError(quizError(failure)); }
    finally { setBusy(false); }
  }
  useEffect(() => {
    if (!dirty && !busy) return;
    const saveLinkNavigation = (event: MouseEvent) => {
      if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || !(event.target instanceof Element)) return;
      const link = event.target.closest<HTMLAnchorElement>("a[href]");
      if (!link || link.classList.contains("quiz-text-link") || link.target === "_blank" || link.hasAttribute("download")) return;
      const destination = new URL(link.href);
      if (destination.origin !== window.location.origin || destination.pathname === window.location.pathname) return;
      event.preventDefault();
      if (!busy) void action(() => router.push(`${destination.pathname}${destination.search}${destination.hash}`));
    };
    document.addEventListener("click", saveLinkNavigation, true);
    return () => document.removeEventListener("click", saveLinkNavigation, true);
  });
  async function submit() { await action(async (saved) => { const result = await completeAttempt(saved.id); clearConfirmedDraft(browserDraftStorage(), result); loaded.setData(result); setConfirm(false); setIndex(0); }); }
  const answered = attempt?.questions.filter((item) => item.selected_keys.length > 0).length ?? 0;
  return <><header className="page-heading resource-heading"><div><h1>{attempt?.title ?? "Quiz attempt"}</h1><p>{completed ? "Results and answer review" : "One question at a time. Save your answer before moving on."}</p></div>{completed ? <Link className="secondary-button" href="/quizzes">Back to quizzes</Link> : <button type="button" className="secondary-button" disabled={busy || !attempt} onClick={() => void action(() => router.push("/quizzes"))}>Save and exit</button>}</header><LoadNotice loading={loaded.loading} error={loaded.error} retry={loaded.retry} />{writeError && !confirm && <p className="auth-error" role="alert">{writeError} Your draft remains on this question.</p>}
    {attempt && question && <>{completed && <div className="quiz-results" role="status"><strong>{attempt.score_percent}%</strong><span>{attempt.score_value} correct out of {attempt.total_questions} questions</span><span>{attempt.questions.filter((item) => reviewQuestion(attempt, item)?.is_correct === false).length} mistakes to review</span></div>}<div className="quiz-taking-progress"><span>Question {index + 1} of {attempt.total_questions}</span><span>{answered} answered</span>{!completed && <span role="status">{busy ? "Saving…" : dirty ? "Unsaved answer" : "Answer saved"}</span>}</div><progress className="quiz-progress" aria-label="Question position" max={attempt.total_questions} value={index + 1} />
    {restored && dirty && <p className="planner-notice" role="status">Unsaved answer restored from this browser session. Save it before continuing.</p>}
    {recoveryUnavailable && dirty && <p className="auth-error" role="alert">Browser draft recovery is unavailable. Save your answer before leaving this page.</p>}
    <AttemptQuestionView attempt={attempt} question={question} selected={completed ? question.selected_keys : draft} change={(keys) => { setRecoveryUnavailable(!rememberAttemptDraft(browserDraftStorage(), attempt, question, keys)); setDraft(keys); setWriteError(null); }} busy={busy} openSource={completed ? undefined : (id) => void action(() => router.push(`/library/${id}`))} />
    <div className="quiz-taking-actions"><button type="button" className="secondary-button" disabled={busy || index === 0} onClick={() => completed ? setIndex(index - 1) : void action(() => setIndex(index - 1))}>Previous question</button>{!completed && <button type="button" className="secondary-button" disabled={busy || !dirty} onClick={() => void action(() => {})}>Save answer</button>}<button type="button" className="primary-button" disabled={busy || index === attempt.questions.length - 1} onClick={() => completed ? setIndex(index + 1) : void action(() => setIndex(index + 1))}>{completed ? "Next question" : "Save and next"}</button>{!completed && <button type="button" className="secondary-button" disabled={busy} onClick={() => { setWriteError(null); setConfirm(true); }}>Submit quiz</button>}</div>
    <nav className="quiz-question-navigation" aria-label="Question navigation">{attempt.questions.map((item, position) => <button type="button" className="secondary-button" key={item.id} disabled={busy} aria-current={position === index ? "step" : undefined} aria-label={`Question ${position + 1}${completed ? reviewQuestion(attempt, item)?.is_correct ? ", correct" : ", incorrect" : item.selected_keys.length ? ", answered" : ", unanswered"}`} onClick={() => completed ? setIndex(position) : void action(() => setIndex(position))}>{position + 1}{!completed && item.selected_keys.length > 0 ? " ✓" : ""}</button>)}</nav></>}
    {confirm && attempt && <QuizDialog title="Submit quiz?" close={() => setConfirm(false)} busy={busy}><p>Your current answer will be saved first. Unanswered questions score zero. After submission, answers cannot be changed.</p><p className="resource-note">{answered} of {attempt.total_questions} questions currently saved with an answer.</p>{writeError && <p className="auth-error" role="alert">{writeError} Submission was not confirmed. Retry to check the saved result.</p>}<div className="planner-dialog-actions"><button className="secondary-button" disabled={busy} onClick={() => setConfirm(false)}>Keep studying</button><button className="primary-button" disabled={busy} onClick={() => void submit()}>{busy ? "Submitting…" : "Save and submit"}</button></div></QuizDialog>}
  </>;
}
