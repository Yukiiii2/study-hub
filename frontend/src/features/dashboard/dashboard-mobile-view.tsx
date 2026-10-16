import Link from "next/link";
import type { DashboardViewProps } from "./dashboard-view";
import { ContentSkeleton, ProgressMeter, StatusBadge } from "@/components/study-ui";
import { InterfaceIcon } from "@/components/interface-icon";
import { dateLabel, zonedParts } from "@/features/study-plan/dates";
import { sessionSpansStudyDays, studyDuration } from "@/features/analytics/presentation";
import { formatDuration } from "@/features/videos/duration";

/** Task-first composition; the parent owns requests, the clock and refresh state. */
export function DashboardMobileView({ data, extras, elapsed = 0, refreshing, extrasLoading, error, extraErrors = [], onRefresh }: DashboardViewProps) {
  const active = extras?.focus?.active_session;
  const next = data?.today_events.filter(event => event.status === "scheduled" && Date.parse(event.end_at) > Date.parse(data.generated_at)).sort((a,b) => Date.parse(a.start_at)-Date.parse(b.start_at))[0];
  const older = !!active && !!extras?.focus && sessionSpansStudyDays(active.started_at, extras.focus.server_now, extras.focus.timezone);
  const nextPath = next ? `/focus?${new URLSearchParams({ study_event_id: next.id, ...(next.occurrence_date ? { occurrence_date: next.occurrence_date } : {}) })}` : "/focus";
  const lecture = data?.subjects.find(subject => subject.id === data.continue_video_subject_id) ?? data?.subjects.find(subject => subject.video_count > 0);
  const assessment = extras?.assessments?.find(item => !item.scheduled_at || Date.parse(item.scheduled_at) >= Date.parse(data?.generated_at ?? ""));
  const time = (instant: string) => zonedParts(instant, data!.timezone).time;
  const started = active && extras?.focus ? new Intl.DateTimeFormat("en", { timeZone: extras.focus.timezone, month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }).format(new Date(active.started_at)) : "";
  return <div className="mobile-today study-dashboard">
    <header className="mobile-page-intro"><div><h1>Your study day</h1><p>{data ? dateLabel(data.date, {weekday:"long",month:"long",day:"numeric"}) : "Your CPALE review workspace"}</p></div><button className="ghost-button icon-button" aria-label="Refresh dashboard" disabled={refreshing} aria-busy={refreshing} onClick={onRefresh}><InterfaceIcon name="refresh" /></button></header>
    {error && <div className="resource-error"><p role="alert">{error}{data && " Showing the last loaded dashboard."}</p><button className="secondary-button" onClick={onRefresh}>Try again</button></div>}
    {extraErrors.length > 0 && <p className="resource-note" role="alert">{extraErrors.join(", ")} could not refresh. Saved values remain visible. Use Refresh to retry.</p>}
    {!data ? !error && <ContentSkeleton layout="dashboard" /> : <>
      <section className="mobile-next" aria-labelledby="mobile-now"><header><h2 id="mobile-now">Now / Next</h2>{active && <StatusBadge tone={older ? "warning" : "success"}>{older ? "Still open" : "Active"}</StatusBadge>}</header>
        <p className="mobile-context-line">{active ? `${data.subjects.find(subject => subject.id === active.subject_id)?.code ?? "General study"} · ${active.activity_type}` : next ? `${next.subject_code ?? "General study"} · ${time(next.start_at)}` : "Ready when you are"}</p>
        <h3>{active ? older ? "Session still open" : "Your Focus session" : next?.title ?? "Choose your next study block"}</h3>
        {active ? <><p>Started {started}</p><strong className="mobile-elapsed" aria-label="Active session elapsed time">{studyDuration(elapsed)}</strong><p className="resource-note">{older ? "This session began on an earlier day. Check it before recording the final duration." : "Your session is recording. Finish it in Focus to save the duration."}</p></> : <p>{next?.topic_title ?? "Use your plan or start independently with a subject and activity."}</p>}
        <Link className="primary-button" href={active ? "/focus" : nextPath}><InterfaceIcon name="focus" />{active ? older ? "Review open session" : "Resume session" : "Start Focus"}</Link>
      </section>
      <section className="mobile-today-section"><header><h2>Today</h2><Link href="/study-plan">Open plan</Link></header>{data.today_events.length ? <ul className="mobile-day-events">{data.today_events.map(event => <li key={`${event.id}/${event.occurrence_date ?? "one"}`}><time dateTime={event.start_at}>{time(event.start_at)}</time><div><Link href="/study-plan">{event.title}</Link><p>{event.subject_code ?? "General study"}{event.topic_title && ` · ${event.topic_title}`}</p><StatusBadge tone={event.status === "completed" ? "success" : "neutral"}>{event.status}</StatusBadge></div></li>)}</ul> : <p className="mobile-empty">No study blocks planned. <Link href="/study-plan">Plan your day</Link>.</p>}</section>
      <section className="mobile-today-section"><header><h2>Needs attention</h2></header><Link className="mobile-attention-link" href="/recall"><strong>{data.recall_summary.overdue + data.recall_summary.due_today} recall cards due</strong><span>{data.recall_summary.overdue} overdue · {data.recall_summary.due_today} today</span><InterfaceIcon name="next" /></Link>
        {data.upcoming_tasks.length ? <ul className="mobile-task-list">{data.upcoming_tasks.map(task => <li key={task.id}><Link href="/study-plan">{task.title}</Link><p>{task.subject_code ?? "General study"}{task.due_at && ` · Due ${dateLabel(zonedParts(task.due_at,data.timezone).date)}`}</p></li>)}</ul> : <p className="resource-note">No pending tasks.</p>}
        {assessment && <Link className="mobile-attention-link" href={`/assessments/${assessment.id}`}><strong>{assessment.title}</strong><span>{assessment.scheduled_at ? dateLabel(zonedParts(assessment.scheduled_at,data.timezone).date) : "Assessment date not set"}</span><InterfaceIcon name="next" /></Link>}
      </section>
      <section className="mobile-today-section"><header><h2>Continue studying</h2></header>{lecture ? <Link className="mobile-attention-link" data-subject={lecture.code} href={`/subjects/${lecture.id}/videos`}><strong><span className="subject-marker" aria-hidden="true" />{lecture.code} lectures</strong><span>{lecture.completed_video_count} / {lecture.video_count} completed</span><InterfaceIcon name="next" /></Link> : <Link className="secondary-button" href="/subjects">Browse subjects</Link>}</section>
      <section className="mobile-today-section"><header><h2>Progress at a glance</h2><Link href="/analytics">Analytics</Link></header><dl className="mobile-progress-summary"><div><dt>Study today</dt><dd>{extras?.focus ? studyDuration(extras.focus.today_seconds) : extrasLoading ? "Updating…" : "Unavailable"}</dd></div><div><dt>Lectures completed</dt><dd>{data.video_summary.completed_videos} / {data.video_summary.total_videos}</dd></div></dl><p className="resource-note">{formatDuration(data.video_summary.remaining_duration_seconds)} of known lecture duration remaining.</p>
        {extras?.activity && <details><summary>Seven-day study activity</summary><ol className="mobile-week-values">{extras.activity.daily.map(day => <li key={day.date}><time dateTime={day.date}>{dateLabel(day.date,{weekday:"short"})}</time><span>{studyDuration(day.duration_seconds)}</span></li>)}</ol></details>}
      </section>
      <section className="mobile-today-section"><header><h2>Subjects</h2><Link href="/subjects">All subjects</Link></header><ul className="mobile-subject-overview">{data.subjects.map(subject => <li data-subject={subject.code} key={subject.id}><Link href={`/subjects/${subject.id}`}><span className="subject-marker" aria-hidden="true" />{subject.code}<span>{subject.topic_count} topics</span></Link><ProgressMeter label="Lectures" value={subject.completed_video_count} total={subject.video_count} /></li>)}</ul></section>
    </>}
  </div>;
}
