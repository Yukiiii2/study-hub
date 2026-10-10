"use client";

import Link from "next/link";
import { PageHeader } from "@/components/page-header";
import { StatusBadge } from "@/components/study-ui";
import { useCallback, useState } from "react";
import { archiveQuestion, getQuestions, quizError, type Question } from "@/services/quizzes";
import { getSubjects } from "@/services/subjects";
import { LoadNotice, Pagination, QuizDialog, useQuizLoad } from "./shared";
import { QuestionEditor } from "./question-editor";
import { QuestionImport } from "./question-import";

export function QuestionBank() {
  const [filters, setFilters] = useState({ q: "", subject_id: "", question_type: "", offset: 0 });
  const [search, setSearch] = useState("");
  const [editor, setEditor] = useState<Question | "new" | null>(null);
  const [importing, setImporting] = useState(false);
  const [archive, setArchive] = useState<Question | null>(null);
  const [busy, setBusy] = useState(false);
  const [writeError, setWriteError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const subjects = useQuizLoad(useCallback((signal) => getSubjects(signal), []));
  const list = useQuizLoad(useCallback(async (signal) => ({ ...(await getQuestions({ ...filters, limit: 20 }, signal)), offset: filters.offset, filters }), [filters]));
  async function confirmArchive() { if (!archive) return; setBusy(true); setWriteError(null); try { await archiveQuestion(archive.id); setArchive(null); setNotice("Question archived. Existing attempts retain their saved question."); list.retry(); } catch (failure) { setWriteError(quizError(failure)); } finally { setBusy(false); } }
  return <><Link className="back-link" href="/quizzes">Back to quizzes</Link><PageHeader title="Question bank" description="Write, organize and import your study questions." actions={<><button className="secondary-button" onClick={() => setImporting(true)}>Import CSV</button><button className="primary-button" onClick={() => setEditor("new")}>New question</button></>} />{notice && <p className="planner-notice" role="status">{notice}</p>}
    <form className="resource-filters ui-toolbar quiz-management-toolbar" onSubmit={(event) => { event.preventDefault(); setFilters({ ...filters, q: search.trim(), offset: 0 }); }}><label className="resource-search">Search questions<input type="search" maxLength={200} value={search} onChange={(event) => setSearch(event.target.value)} /></label><label>Subject<select value={filters.subject_id} disabled={!subjects.data} onChange={(event) => setFilters({ ...filters, subject_id: event.target.value, offset: 0 })}><option value="">All subjects</option>{subjects.data?.map((item) => <option key={item.id} value={item.id}>{item.code}</option>)}</select></label><label>Type<select value={filters.question_type} onChange={(event) => setFilters({ ...filters, question_type: event.target.value, offset: 0 })}><option value="">All types</option><option value="single_select">Single select</option><option value="multi_select">Multi select</option><option value="true_false">True / false</option></select></label><button className="secondary-button">Search</button></form>
    <LoadNotice loading={false} error={subjects.error} retry={subjects.retry} /><LoadNotice loading={list.loading} error={list.error} retry={list.retry} />{list.data?.filters !== filters && list.data && <p className="resource-note">Showing the last loaded questions while filters refresh.</p>}{list.data && <>{!list.data.questions.length && <div className="resource-empty"><h2>No questions match this view</h2><p>Create a question or adjust the filters.</p><button className="secondary-button" onClick={() => setEditor("new")}>New question</button></div>}<ul className="quiz-list">{list.data.questions.map((question) => <li className="quiz-row" key={question.id}><div className="quiz-row-copy"><strong>{question.prompt}</strong><span className="quiz-row-meta"><StatusBadge>{question.question_type.replaceAll("_", " ")}</StatusBadge><span>{question.origin}{question.subject_id ? ` · ${subjects.data?.find((item) => item.id === question.subject_id)?.code ?? "Subject linked"}` : ""}</span></span><span className="quiz-answer-summary">Correct: {question.correct_keys.join(", ")}</span></div><div className="resource-actions"><button type="button" className="secondary-button" onClick={() => setEditor(question)}>Edit</button><button type="button" className="ghost-button" onClick={() => { setWriteError(null); setArchive(question); }}>Archive</button></div></li>)}</ul><Pagination offset={list.data.offset} total={list.data.total} busy={list.loading} change={(offset) => setFilters({ ...filters, offset })} /></>}
    {editor && <QuestionEditor question={editor === "new" ? undefined : editor} close={() => setEditor(null)} saved={() => { setNotice("Question saved."); list.retry(); }} />}{importing && <QuestionImport close={() => setImporting(false)} saved={(message) => { setNotice(message); list.retry(); }} />}{archive && <QuizDialog title="Archive question?" close={() => setArchive(null)} busy={busy}><p>This question will leave the bank and cannot be added to new quizzes. Existing attempt history is preserved.</p>{writeError && <p role="alert" className="auth-error">{writeError}</p>}<div className="planner-dialog-actions"><button className="secondary-button" disabled={busy} onClick={() => setArchive(null)}>Keep question</button><button className="danger-button" disabled={busy} onClick={() => void confirmArchive()}>{busy ? "Archiving…" : "Archive question"}</button></div></QuizDialog>}
  </>;
}
