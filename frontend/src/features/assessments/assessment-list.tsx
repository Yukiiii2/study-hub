"use client";

import Link from "next/link";
import { PageHeader } from "@/components/page-header";
import { StatusBadge } from "@/components/study-ui";
import { useRouter } from "next/navigation";
import { useCallback, useState } from "react";
import { getAssessments, type AssessmentStatus } from "@/services/assessments";
import { getPlannerContext } from "@/services/study-plan";
import { LoadNotice, Pagination, useQuizLoad } from "@/features/quizzes/shared";
import { AssessmentEditor } from "./assessment-editor";
import { assessmentTimestamp } from "./form-state";
import { assessmentLoad } from "./load";

export function AssessmentListPage() {
  const router = useRouter();
  const [filters, setFilters] = useState<{ q: string; status: AssessmentStatus | "all"; offset: number }>({ q: "", status: "all", offset: 0 });
  const [search, setSearch] = useState(""), [creating, setCreating] = useState(false);
  const context = useQuizLoad(useCallback((signal) => assessmentLoad(getPlannerContext(signal)), []));
  const assessments = useQuizLoad(useCallback((signal) => assessmentLoad(getAssessments({ ...filters, limit: 20 }, signal).then((data) => ({ ...data, filters }))), [filters]));
  const timezone = context.data?.timezone;
  return <><PageHeader title="Assessments" description="Plan your coverage and keep a separate history of assessment results." actions={<button type="button" className="primary-button" disabled={!timezone || context.loading || !!context.error} onClick={() => setCreating(true)}>New assessment</button>} /><form className="resource-filters ui-toolbar assessment-management-toolbar" onSubmit={(event) => { event.preventDefault(); setFilters({ ...filters, q: search.trim(), offset: 0 }); }}><label className="resource-search">Search assessments<input type="search" maxLength={200} value={search} onChange={(event) => setSearch(event.target.value)} /></label><label>Status<select value={filters.status} onChange={(event) => setFilters({ ...filters, status: event.target.value as AssessmentStatus | "all", offset: 0 })}><option value="all">All current statuses</option><option value="planned">Planned</option><option value="completed">Completed</option><option value="cancelled">Cancelled</option><option value="archived">Archived</option></select></label><button className="secondary-button" disabled={assessments.loading}>Search</button></form><p className="resource-note">{timezone ? `Dates use ${timezone}.` : "Loading your profile timezone before displaying dates or creating an assessment."} Archived definitions retain their result history.</p><LoadNotice loading={context.loading} error={context.error} retry={context.retry} /><LoadNotice loading={assessments.loading} error={assessments.error} retry={assessments.retry} />{!assessments.loading && !assessments.error && assessments.data?.filters === filters && <>{!assessments.data.assessments.length ? <div className="resource-empty"><h2>No assessments match this view</h2><p>Create an assessment or adjust the status and search filters.</p></div> : <ul className="quiz-list assessment-list">{assessments.data.assessments.map((assessment) => <li className="quiz-row" key={assessment.id}><div className="quiz-row-main assessment-row-copy"><h2><Link href={`/assessments/${assessment.id}`}>{assessment.title}</Link></h2><div className="assessment-row-meta"><p className="resource-note">{assessment.scheduled_at ? timezone ? <><time dateTime={assessment.scheduled_at}>{assessmentTimestamp(assessment.scheduled_at, timezone)}</time>{assessment.status === "planned" && new Date(assessment.scheduled_at).getTime() > Date.now() && " · Upcoming"}</> : "Date awaiting profile timezone" : "Date not set"}</p><StatusBadge tone={assessment.status === "completed" ? "success" : assessment.status === "planned" ? "info" : "neutral"}>{assessment.status}</StatusBadge></div><p className="resource-note">{assessment.topic_count} covered topics{assessment.coverage_subjects.length ? ` · ${assessment.coverage_subjects.map((subject) => `${subject.code}${subject.scope === "all_topics" ? " (all topics)" : " (selected topics)"}`).join(", ")}` : " · Coverage not selected"}</p></div><Link className="secondary-button" href={`/assessments/${assessment.id}`}>View assessment</Link></li>)}</ul>}<Pagination offset={filters.offset} total={assessments.data.total} busy={assessments.loading} change={(offset) => setFilters({ ...filters, offset })} /></>}{creating && timezone && <AssessmentEditor timezone={timezone} close={() => setCreating(false)} saved={(assessment) => router.push(`/assessments/${assessment.id}`)} />}</>;
}
