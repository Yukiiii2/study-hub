import Link from "next/link";
import type { CSSProperties } from "react";
import type { DashboardData } from "@/services/dashboard";
import type { AnalyticsData, FocusData } from "@/services/analytics";
import type { Assessment } from "@/services/assessments";
import { CurriculumLoading } from "@/features/subjects/load-state";
import { dateLabel, zonedParts } from "@/features/study-plan/dates";
import { formatDuration } from "@/features/videos/duration";
import { studyDuration } from "@/features/analytics/presentation";
import { ProgressMeter, StatusBadge } from "@/components/study-ui";
import { InterfaceIcon } from "@/components/interface-icon";

export type DashboardExtras = { focus: FocusData | null; activity: AnalyticsData | null; assessments: Assessment[] | null };
type Props = { data: DashboardData | null; refreshing: boolean; error: string | null; onRefresh: () => void; extras?: DashboardExtras; extrasLoading?: boolean; elapsed?: number; extraErrors?: string[] };
function hoursMinutes(seconds: number) { const minutes = Math.floor(seconds / 60); return `${Math.floor(minutes / 60)}h ${String(minutes % 60).padStart(2, "0")}m`; }

export function DashboardView({ data, refreshing, error, onRefresh, extras, extrasLoading = false, elapsed = 0, extraErrors = [] }: Props) {
  const summary = data?.video_summary;
  const focus = extras?.focus, activity = extras?.activity, active = focus?.active_session;
  const videoSubject = data?.continue_video_subject_id ?? data?.subjects.find(subject => subject.video_count > 0)?.id;
  const videoPath = videoSubject ? `/subjects/${encodeURIComponent(videoSubject)}/videos` : null;
  const hour = data ? Number(zonedParts(data.generated_at, data.timezone).time.slice(0, 2)) : null;
  const greeting = hour === null ? "Your study day" : hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";
  const next = data?.today_events.filter(event => event.status === "scheduled" && Date.parse(event.end_at) > Date.parse(data.generated_at)).sort((a,b) => Date.parse(a.start_at)-Date.parse(b.start_at))[0];
  const nextPath = next ? `/focus?${new URLSearchParams({ study_event_id: next.id, ...(next.occurrence_date ? { occurrence_date: next.occurrence_date } : {}) })}` : "/focus";
  const nextAssessment = extras?.assessments?.find(item => item.scheduled_at && Date.parse(item.scheduled_at) >= Date.parse(data?.generated_at ?? "")) ?? extras?.assessments?.find(item => !item.scheduled_at) ?? extras?.assessments?.[0];
  const unavailable = extrasLoading ? "Loading…" : "Unavailable";
  const maxDay = Math.max(3600, ...(activity?.daily.map(day => day.duration_seconds) ?? []));
  const subjectColors = new Map(data?.subjects.map(subject => [subject.id, subject.color_key]));
  function eventTime(instant: string) { const parts = zonedParts(instant, data!.timezone); return parts.date === data!.date ? parts.time : `${dateLabel(parts.date)} ${parts.time}`; }
  function fullDate(instant: string) { return new Intl.DateTimeFormat("en", { timeZone: data!.timezone, year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).format(new Date(instant)); }

  return <div className="study-dashboard">
    <header className="dash-welcome"><div><h1>{greeting}</h1><p>{data ? <time dateTime={data.date}>{dateLabel(data.date, { weekday: "long", month: "long", day: "numeric" })}</time> : "Your CPALE review workspace"}</p></div><div className="dash-header-actions"><Link className="secondary-button" href="/study-plan">View full plan</Link><button className="ghost-button icon-button" aria-busy={refreshing} aria-label={refreshing ? "Refreshing dashboard" : "Refresh dashboard"} disabled={refreshing} onClick={onRefresh}><InterfaceIcon name="refresh" /></button></div></header>
    {error && <div className="resource-error"><p className="auth-error" role="alert">{error} {data && "Showing the last loaded dashboard."}</p><button className="secondary-button" onClick={onRefresh}>Try again</button></div>}
    {extraErrors.length > 0 && <p className="resource-note" role="alert">{extraErrors.join(", ")} could not refresh. Showing saved values where available. Use Refresh to retry.</p>}
    {data === null ? !error && <CurriculumLoading layout="dashboard" /> : <>
      <section className="study-docket" aria-labelledby="dashboard-now">
        <header><span className="docket-indicator" aria-hidden="true" /><h2 id="dashboard-now">Now / Next</h2>{active && <StatusBadge tone="success">Session active</StatusBadge>}</header>
        <div className="docket-body">
          <div className="docket-time">{active ? <strong aria-label="Active session elapsed time">{studyDuration(elapsed).padStart(8, "0")}</strong> : next ? <><strong>{eventTime(next.start_at)}</strong><span>{eventTime(next.end_at)}</span></> : <InterfaceIcon name="focus" />}</div>
          <div className="docket-copy"><div className="docket-context">{active ? `${data.subjects.find(subject => subject.id === active.subject_id)?.code ?? "General study"} / ${active.activity_type}` : next ? <><span className="subject-marker" data-color={subjectColors.get(next.subject_id ?? "") ?? undefined} aria-hidden="true" />{next.subject_code ?? "General study"} <span>{next.event_type}</span></> : "Your next step"}</div><h2>{active ? "Continue your focused session" : next?.title ?? "Choose a study block and settle in"}</h2><p>{active ? "Your session is still recording. Return when you are ready to finish." : next?.topic_title ?? "Start independently or use your study plan for context."}</p></div>
          <Link className="primary-button" href={active ? "/focus" : nextPath}><InterfaceIcon name="focus" />{active ? "Return to session" : "Start Focus"}</Link>
        </div>
        <footer>{focus ? active ? "Active session restored from your saved study state." : "No active session" : extrasLoading ? "Loading session…" : "Session unavailable — open Focus to check."}<span>{data.timezone}</span></footer>
      </section>
      <div className="desk-day-grid">
        <section className="desk-schedule" aria-labelledby="dashboard-today"><header className="dash-section-header"><div><h2 id="dashboard-today">Today</h2><p>{data.today_events.length} planned study {data.today_events.length === 1 ? "block" : "blocks"}</p></div><Link href="/study-plan">Open plan<InterfaceIcon name="next" /></Link></header>
          {data.today_events.length === 0 ? <div className="desk-empty"><h3>Your schedule is clear.</h3><p>Create a study block when you know what to work on.</p><Link className="secondary-button" href="/study-plan">Plan study block</Link></div> : <ul className="desk-agenda">{data.today_events.map(event => <li key={`${event.id}/${event.occurrence_date ?? "one"}`}><div className="desk-time"><time dateTime={event.start_at}>{eventTime(event.start_at)}</time><time dateTime={event.end_at}>{eventTime(event.end_at)}</time></div><span className="subject-marker" data-color={subjectColors.get(event.subject_id ?? "") ?? undefined} aria-hidden="true" /><div><Link href="/study-plan">{event.title}</Link><p>{event.subject_code ?? "General study"} · {event.event_type}{event.topic_title && ` · ${event.topic_title}`}{event.is_recurring && " · Repeats"}</p></div><StatusBadge tone={event.status === "completed" ? "success" : "neutral"}>{event.status[0].toUpperCase() + event.status.slice(1)}</StatusBadge></li>)}</ul>}
        </section>
        <section className="desk-attention" aria-labelledby="dashboard-attention"><header className="dash-section-header"><div><h2 id="dashboard-attention">Needs attention</h2><p>Due work and your next milestones</p></div></header>
          <section id="dashboard-recall" className="attention-row"><span className="attention-count" data-tone="warning">{data.recall_summary.overdue + data.recall_summary.due_today}</span><div><Link href="/recall">{data.recall_summary.overdue + data.recall_summary.due_today ? "Recall cards ready" : "No cards due — open recall"}</Link><p>{data.recall_summary.overdue} overdue · {data.recall_summary.due_today} due today</p></div><InterfaceIcon name="next" /></section>
          <section id="dashboard-tasks" className="attention-tasks"><h3>Tasks</h3>{data.upcoming_tasks.length ? <ul>{data.upcoming_tasks.map(task => <li key={task.id}><Link href="/study-plan">{task.title}</Link><p>{task.subject_code ?? "General study"}{task.topic_title && ` · ${task.topic_title}`}{task.estimated_minutes ? ` · ${task.estimated_minutes} min planned` : ""}</p><div>{task.due_at ? <><time dateTime={task.due_at}>{fullDate(task.due_at)}</time>{Date.parse(task.due_at) < Date.parse(data.generated_at) && <StatusBadge tone="danger">Overdue</StatusBadge>}</> : <span>No due date</span>}</div></li>)}</ul> : <p>No pending tasks. Your next study block can start with a clear plan.</p>}</section>
          <section className="attention-assessment"><h3>Assessment</h3>{extras?.assessments ? nextAssessment ? <><Link href={`/assessments/${encodeURIComponent(nextAssessment.id)}`}>{nextAssessment.title}</Link><p>{nextAssessment.scheduled_at ? <time dateTime={nextAssessment.scheduled_at}>{fullDate(nextAssessment.scheduled_at)}</time> : "No date set"}</p>{nextAssessment.scheduled_at && Date.parse(nextAssessment.scheduled_at) < Date.parse(data.generated_at) && <StatusBadge tone="warning">Past scheduled date</StatusBadge>}</> : <p>No planned assessments.</p> : <p>{extrasLoading ? "Loading assessments…" : "Assessment dates unavailable."}</p>}<Link className="quiz-text-link" href="/assessments">View assessments</Link></section>
        </section>
      </div>
      <section className="desk-continue" aria-labelledby="dashboard-continue"><InterfaceIcon name="subjects" /><div><h2 id="dashboard-continue">Continue studying</h2><p>{videoSubject ? `${data.subjects.find(subject => subject.id === videoSubject)?.code ?? "Subject"} lecture workspace` : "Explore your curriculum"}</p><span>Lecture progress uses saved completion states.</span></div>{videoPath ? <Link className="secondary-button" href={videoPath}>{data.continue_video_subject_id ? "Continue Videos" : "Browse Videos"}</Link> : <Link className="secondary-button" href="/subjects">Browse subjects</Link>}</section>
      <div className="desk-progress-grid">
        <section className="desk-progress" aria-label="Study overview"><header className="dash-section-header"><div><h2>Progress at a glance</h2><p>Recorded activity, kept separate from planned time</p></div><Link href="/analytics">Analytics<InterfaceIcon name="next" /></Link></header>
          <dl className="desk-summary"><div><dt>Study today</dt><dd>{focus ? hoursMinutes(focus.today_seconds) : unavailable}</dd><small>{focus ? `${focus.today_session_count} sessions` : "Recorded study time unavailable"}</small></div><div><dt>Lectures completed</dt><dd>{summary!.completed_videos} / {summary!.total_videos}</dd><small>{summary!.remaining_videos} remaining</small></div><div><dt>Recall queue</dt><dd>{data.recall_summary.due_today + data.recall_summary.overdue} due</dd><small>{data.recall_summary.overdue} overdue</small></div></dl>
          <section className="desk-week" aria-labelledby="dashboard-week"><header><h3 id="dashboard-week">Seven-day activity</h3><span>{activity ? hoursMinutes(activity.summary.total_seconds) : unavailable}</span></header>{activity ? <ol className="desk-week-bars" aria-label="Daily recorded study time">{activity.daily.map(day => <li key={day.date} data-today={day.date === data.date || undefined}><span>{hoursMinutes(day.duration_seconds)}</span><div className="desk-day-track" aria-hidden="true"><i style={{ "--day-height": `${day.duration_seconds / maxDay * 100}%` } as CSSProperties} /></div><time dateTime={day.date}>{dateLabel(day.date, { weekday: "short" })}</time></li>)}</ol> : <p>{extrasLoading ? "Loading weekly study time…" : "Weekly study time is unavailable. Refresh to try again."}</p>}</section>
          <details className="desk-duration" id="dashboard-videos"><summary>Known lecture duration totals</summary><dl><div><dt>Completed</dt><dd>{formatDuration(summary!.completed_duration_seconds)}</dd></div><div><dt>Remaining</dt><dd>{formatDuration(summary!.remaining_duration_seconds)}</dd></div></dl><p>Known lecture durations, separate from recorded study time.</p>{summary!.unknown_duration_videos > 0 && <p>{summary!.unknown_duration_videos} {summary!.unknown_duration_videos === 1 ? "video without a duration" : "videos without a duration"} excluded.</p>}</details>
        </section>
        <section className="desk-subjects" aria-labelledby="dashboard-subjects"><header className="dash-section-header"><div><h2 id="dashboard-subjects">Subjects</h2><p>Lectures and curriculum</p></div><Link href="/subjects">All subjects</Link></header>{data.subjects.length ? <ul>{data.subjects.map(subject => <li key={subject.id} data-subject={subject.code}><Link href={`/subjects/${encodeURIComponent(subject.id)}`} title={subject.name}><span className="subject-marker" aria-hidden="true" />{subject.code}</Link><div><ProgressMeter value={subject.completed_video_count} total={subject.video_count} label={`${subject.code} videos completed`} tone="info" /><span>{subject.topic_count} {subject.topic_count === 1 ? "topic" : "topics"}</span></div><Link className="desk-subject-open" href={`/subjects/${encodeURIComponent(subject.id)}/videos`} aria-label={`Browse ${subject.code} videos`}><InterfaceIcon name="next" /></Link></li>)}</ul> : <p>No active subjects available.</p>}</section>
      </div>
      <nav className="desk-tools" aria-label="Quick actions"><Link href="/focus">Start focus</Link><Link href="/study-plan">Plan study</Link><Link href="/recall">Review recall</Link><Link href="/quizzes">Practice quiz</Link><Link href="/library">Upload resource</Link></nav>
    </>}
  </div>;
}
