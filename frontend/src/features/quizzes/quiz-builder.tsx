"use client";

import Link from "next/link";
import { PageHeader } from "@/components/page-header";
import { SectionHeader, StatusBadge } from "@/components/study-ui";
import { useRouter } from "next/navigation";
import { useCallback, useState } from "react";
import { archiveQuiz, createQuiz, getQuestions, getQuiz, quizError, startAttempt, updateQuiz, type QuizDetail, type QuizInput } from "@/services/quizzes";
import { Associations, LoadNotice, Pagination, QuizDialog, useQuizLoad } from "./shared";

type SelectedQuestion = QuizDetail["questions"][number];
export function QuizDetailPage({ quizId }: { quizId: string }) {
  const quiz = useQuizLoad(useCallback((signal) => getQuiz(quizId, signal), [quizId]));
  return <><LoadNotice loading={quiz.loading} error={quiz.error} retry={quiz.retry} />{quiz.data && <QuizBuilder seed={quiz.data} />}</>;
}
export function QuizBuilder({ seed = null }: { seed?: QuizDetail | null }) {
  const router = useRouter();
  const [quiz, setQuiz] = useState(seed);
  const [title, setTitle] = useState(seed?.title ?? "");
  const [description, setDescription] = useState(seed?.description ?? "");
  const [subject, setSubject] = useState(seed?.subject_id ?? "");
  const [topic, setTopic] = useState(seed?.topic_id ?? "");
  const [selected, setSelected] = useState<SelectedQuestion[]>(seed?.questions ?? []);
  const [filters, setFilters] = useState({ q: "", offset: 0 });
  const [search, setSearch] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [archiving, setArchiving] = useState(false);
  const available = useQuizLoad(useCallback(async (signal) => ({ ...(await getQuestions({ ...filters, subject_id: subject, topic_id: topic, limit: 20 }, signal)), filters, subject, topic }), [filters, subject, topic]));
  function move(index: number, direction: number) { const next = [...selected]; [next[index], next[index + direction]] = [next[index + direction], next[index]]; setSelected(next); setNotice(null); }
  async function persist() {
    if (!title.trim() || !selected.length) throw new Error("Enter a quiz title and add at least one question.");
    const input: QuizInput = { title: title.trim(), description: description.trim() || null, subject_id: subject || null, topic_id: topic || null, question_ids: selected.map((question) => question.id) };
    const result = quiz ? await updateQuiz(quiz.id, input) : await createQuiz(input);
    setQuiz(result); setNotice("Quiz saved."); return result;
  }
  async function save(start = false) {
    if (!title.trim() || !selected.length) { setError("Enter a quiz title and add at least one question."); return; }
    setBusy(true); setError(null); setNotice(null);
    try { const result = await persist(); if (start) { const attempt = await startAttempt(result.id); router.push(`/quizzes/attempts/${attempt.id}`); } else if (!seed) router.replace(`/quizzes/${result.id}`); }
    catch (failure) { setError(quizError(failure)); } finally { setBusy(false); }
  }
  async function resume() { if (!quiz) return; setBusy(true); setError(null); try { const attempt = await startAttempt(quiz.id); router.push(`/quizzes/attempts/${attempt.id}`); } catch (failure) { setError(quizError(failure)); } finally { setBusy(false); } }
  async function confirmArchive() { if (!quiz) return; setBusy(true); setError(null); try { await archiveQuiz(quiz.id); router.push("/quizzes"); } catch (failure) { setError(quizError(failure)); } finally { setBusy(false); } }
  return <><Link className="back-link" href="/quizzes">Back to quizzes</Link><PageHeader title={seed ? "Edit quiz" : "New quiz"} description="Choose questions and arrange the order for your practice session." meta={quiz?.is_archived ? <StatusBadge>Archived</StatusBadge> : <StatusBadge tone="info">{selected.length} questions selected</StatusBadge>} />{notice && <p className="planner-notice" role="status">{notice}</p>}{error && !archiving && <p className="auth-error" role="alert">{error}</p>}
    <form className="quiz-builder-form quiz-builder-workspace" onSubmit={(event) => { event.preventDefault(); void save(); }}><fieldset className="planner-form-grid quiz-details-form ui-panel" disabled={busy || !!quiz?.is_archived}><label className="planner-wide">Title<input required maxLength={200} value={title} onChange={(event) => { setTitle(event.target.value); setNotice(null); }} /></label><label className="planner-wide">Description (optional)<textarea maxLength={2000} rows={2} value={description} onChange={(event) => { setDescription(event.target.value); setNotice(null); }} /></label><Associations subject={subject} topic={topic} changeSubject={(id) => { setSubject(id); setFilters({ ...filters, offset: 0 }); setNotice(null); }} changeTopic={(id) => { setTopic(id); setFilters({ ...filters, offset: 0 }); setNotice(null); }} disabled={busy} /></fieldset>
    <section className="quiz-selection" aria-labelledby="selected-title"><SectionHeader titleId="selected-title" title="Quiz order" detail="Questions appear in this order during practice." actions={<StatusBadge>{selected.length} / 100</StatusBadge>} />{!selected.length && <p className="resource-note">Add questions from the bank below.</p>}<ol className="quiz-list quiz-ordered">{selected.map((question, index) => <li className="quiz-row" key={question.id}><div className="quiz-row-copy"><strong>{index + 1}. {question.prompt}</strong><span>{question.question_type.replaceAll("_", " ")}</span></div><div className="resource-actions"><button type="button" className="secondary-button" disabled={busy || index === 0 || !!quiz?.is_archived} aria-label={`Move question ${index + 1} up`} onClick={() => move(index, -1)}>Up</button><button type="button" className="secondary-button" disabled={busy || index === selected.length - 1 || !!quiz?.is_archived} aria-label={`Move question ${index + 1} down`} onClick={() => move(index, 1)}>Down</button><button type="button" className="secondary-button" disabled={busy || !!quiz?.is_archived} aria-label={`Remove question ${index + 1}`} onClick={() => { setSelected(selected.filter((item) => item.id !== question.id)); setNotice(null); }}>Remove</button></div></li>)}</ol></section>
    <div className="quiz-builder-actions"><button className="secondary-button" disabled={busy || !!quiz?.is_archived}>{busy ? "Working…" : "Save quiz"}</button><button type="button" className="primary-button" disabled={busy || !selected.length || !!quiz?.is_archived} onClick={() => void save(true)}>Save and start</button>{quiz?.active_attempt_id && <button type="button" className="secondary-button" disabled={busy || !!quiz.is_archived} onClick={() => void resume()}>Resume saved attempt</button>}{quiz && !quiz.is_archived && <button type="button" className="danger-button" disabled={busy} onClick={() => { setError(null); setArchiving(true); }}>Archive quiz</button>}</div>{quiz?.active_attempt_id && <p className="resource-note">The active attempt keeps its original questions. Resume opens that saved attempt.</p>}{quiz?.is_archived && <p className="resource-note">This quiz is archived. Its attempts remain in history.</p>}</form>
    {!quiz?.is_archived && <section className="quiz-available" aria-labelledby="available-title"><SectionHeader titleId="available-title" title="Add from question bank" /><p className="resource-note">Subject and topic selections filter the bank. Changing them does not remove questions already in the quiz.</p><form className="resource-filters ui-toolbar quiz-management-toolbar" onSubmit={(event) => { event.preventDefault(); setFilters({ q: search.trim(), offset: 0 }); }}><label className="resource-search">Search questions<input type="search" maxLength={200} value={search} onChange={(event) => setSearch(event.target.value)} /></label><button className="secondary-button">Search</button><Link className="secondary-button" href="/question-bank">Manage bank</Link></form><LoadNotice loading={available.loading} error={available.error} retry={available.retry} />{available.data && <>{(available.data.filters !== filters || available.data.subject !== subject || available.data.topic !== topic) && <p className="resource-note">Showing the last loaded questions while filters refresh.</p>}{!available.data.questions.length && <p className="resource-note">No questions match. Create questions in the bank or change the filters.</p>}<ul className="quiz-list">{available.data.questions.map((question) => { const added = selected.some((item) => item.id === question.id); return <li className="quiz-row" data-added={added} key={question.id}><div className="quiz-row-copy"><strong>{question.prompt}</strong><span>{question.question_type.replaceAll("_", " ")}</span></div><button type="button" className="secondary-button" disabled={added || busy || selected.length >= 100} onClick={() => { setSelected([...selected, question]); setNotice(null); }}>{added ? "Added" : "Add question"}</button></li>; })}</ul><Pagination offset={available.data.filters.offset} total={available.data.total} busy={available.loading} change={(offset) => setFilters({ ...filters, offset })} /></>}</section>}
    {archiving && <QuizDialog title="Archive quiz?" busy={busy} close={() => setArchiving(false)}><p>The quiz leaves the active list. Your attempt history remains available.</p>{error && <p className="auth-error" role="alert">{error}</p>}<div className="planner-dialog-actions"><button className="secondary-button" disabled={busy} onClick={() => setArchiving(false)}>Keep quiz</button><button className="danger-button" disabled={busy} onClick={() => void confirmArchive()}>{busy ? "Archiving…" : "Archive quiz"}</button></div></QuizDialog>}
  </>;
}
