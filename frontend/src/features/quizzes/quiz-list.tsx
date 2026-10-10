"use client";

import Link from "next/link";
import { PageHeader } from "@/components/page-header";
import { SectionHeader, StatusBadge } from "@/components/study-ui";
import { useCallback, useState } from "react";
import { getAttempts, getQuizzes } from "@/services/quizzes";
import { getSubjects } from "@/services/subjects";
import { useResourceTimezone as useQuizTimezone } from "@/features/resources/use-resource-timezone";
import { LoadNotice, Pagination, useQuizLoad } from "./shared";

export function quizTimestamp(value: string, timezone: string) {
  return new Intl.DateTimeFormat("en", { timeZone: timezone, month: "short", day: "numeric", year: "numeric", hour: "numeric", minute: "2-digit" }).format(new Date(value));
}

export function QuizListPage() {
  const [filters, setFilters] = useState({ subject_id: "", q: "", offset: 0 });
  const [search, setSearch] = useState("");
  const [historyOffset, setHistoryOffset] = useState(0);
  const { timezone, timezoneNote, timezoneFailed, retryTimezone } = useQuizTimezone();
  const subjects = useQuizLoad(useCallback((signal) => getSubjects(signal), []));
  const quizzes = useQuizLoad(useCallback(async (signal) => ({ ...(await getQuizzes({ ...filters, limit: 20 }, signal)), filters }), [filters]));
  const history = useQuizLoad(useCallback(async (signal) => ({ ...(await getAttempts({ offset: historyOffset, limit: 20 }, signal)), offset: historyOffset }), [historyOffset]));
  return <><PageHeader title="Quizzes" description="Build a focused practice set, then review your answers." actions={<><Link className="secondary-button" href="/question-bank">Question bank</Link><Link className="primary-button" href="/quizzes/new">New quiz</Link></>} />
    <form className="resource-filters ui-toolbar quiz-management-toolbar" onSubmit={(event) => { event.preventDefault(); setFilters({ ...filters, q: search.trim(), offset: 0 }); }}><label className="resource-search">Search quizzes<input type="search" maxLength={200} value={search} onChange={(event) => setSearch(event.target.value)} /></label><label>Subject<select value={filters.subject_id} disabled={!subjects.data} onChange={(event) => setFilters({ ...filters, subject_id: event.target.value, offset: 0 })}><option value="">All subjects</option>{subjects.data?.map((subject) => <option key={subject.id} value={subject.id}>{subject.code}</option>)}</select></label><button className="secondary-button">Search</button></form>
    <LoadNotice loading={false} error={subjects.error} retry={subjects.retry} /><LoadNotice loading={quizzes.loading} error={quizzes.error} retry={quizzes.retry} />{quizzes.data && quizzes.data.filters !== filters && <p className="resource-note">Showing the last loaded quizzes while filters refresh.</p>}{quizzes.data && <>{!quizzes.data.quizzes.length && <div className="resource-empty"><h2>No quizzes in this view</h2><p>Create a quiz from your question bank or adjust the filters.</p><Link className="secondary-button" href="/quizzes/new">New quiz</Link></div>}<ul className="quiz-list">{quizzes.data.quizzes.map((quiz) => <li key={quiz.id} className="quiz-row"><Link className="quiz-row-copy quiz-row-link" href={`/quizzes/${quiz.id}`}><strong>{quiz.title}</strong><span className="quiz-row-meta"><span>{quiz.question_count} questions</span>{quiz.active_attempt_id && <StatusBadge tone="info">In progress</StatusBadge>}</span>{quiz.description && <span>{quiz.description}</span>}</Link>{quiz.active_attempt_id ? <Link className="secondary-button" href={`/quizzes/attempts/${quiz.active_attempt_id}`}>Resume</Link> : <Link className="secondary-button" href={`/quizzes/${quiz.id}`}>Open quiz</Link>}</li>)}</ul><Pagination offset={quizzes.data.filters.offset} total={quizzes.data.total} busy={quizzes.loading} change={(offset) => setFilters({ ...filters, offset })} /></>}
    <section className="quiz-history" aria-labelledby="quiz-history-title"><SectionHeader titleId="quiz-history-title" title="Attempt history" detail="Return to a session or review your completed practice." /><div className="resource-timezone"><p className="resource-note">{timezoneNote}</p>{timezoneFailed && <button type="button" className="secondary-button" onClick={retryTimezone}>Retry timezone</button>}</div><LoadNotice loading={history.loading} error={history.error} retry={history.retry} />{history.data && <>{!history.data.attempts.length && <div className="quiz-history-empty"><p className="resource-note">Your practice history will appear here after you start a quiz.</p></div>}<ul className="quiz-list">{history.data.attempts.map((attempt) => <li className="quiz-row" key={attempt.id}><div className="quiz-row-copy"><strong>{attempt.title}</strong><span className="quiz-row-meta"><StatusBadge tone={attempt.status === "completed" ? "success" : "info"}>{attempt.status === "completed" ? "Completed" : "In progress"}</StatusBadge><span>{attempt.status === "completed" ? `${attempt.score_value} / ${attempt.total_questions} · ${attempt.score_percent}%` : `${attempt.total_questions} questions`}</span></span><span>Started <time dateTime={attempt.started_at}>{quizTimestamp(attempt.started_at, timezone)}</time></span></div><Link className="secondary-button" href={`/quizzes/attempts/${attempt.id}`}>{attempt.status === "completed" ? "Review" : "Resume"}</Link></li>)}</ul><Pagination offset={history.data.offset} total={history.data.total} busy={history.loading} change={setHistoryOffset} /></>}</section>
  </>;
}
