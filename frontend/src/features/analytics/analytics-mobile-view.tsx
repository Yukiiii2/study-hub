import Link from "next/link";
import type { AnalyticsViewProps } from "./use-analytics-data";
import { AnalyticsControls } from "./analytics-controls";
import { DailyChart, TimeBar } from "./analytics-charts";
import { MobileActivityCalendar } from "./mobile-activity-calendar";
import { studyDuration } from "./presentation";
import { SessionList } from "./session-list";
import { dateLabel } from "@/features/study-plan/dates";
import { LoadNotice, Pagination } from "@/features/quizzes/shared";

export function AnalyticsMobileView(model: AnalyticsViewProps) {
  const { summary, history, data, sessions, staleRange, historyStale, subjectMaximum, activityMaximum, plannedMaximum, offset, setOffset } = model;
  return <div className="mobile-analytics">
    <AnalyticsControls model={model} compact />
    <LoadNotice hasData={!!data} loading={summary.loading} error={summary.error} retry={summary.retry} layout="chart" />
    {staleRange && <p className="resource-note" role="status">Updating the selected range. Your last loaded report stays visible.</p>}
    {data && <>
      <p className="resource-note">{dateLabel(data.start_date)} – {dateLabel(data.end_date)} · {data.timezone}</p>
      <section className="mobile-time-summary" aria-label="Study time summary" aria-busy={summary.loading}>
        <p>Completed study time</p><strong className="mobile-total-time">{studyDuration(data.summary.total_seconds)}</strong>
        <dl><div><dt>Sessions</dt><dd>{data.summary.session_count}</dd></div><div><dt>Active days</dt><dd>{data.summary.active_days}</dd></div><div><dt>Average</dt><dd>{studyDuration(data.summary.average_session_seconds)}</dd></div><div><dt>Longest</dt><dd>{studyDuration(data.summary.longest_session_seconds)}</dd></div></dl>
        <p className="resource-note">Finished sessions only. Time shown as h:mm:ss.</p>
      </section>
      <section className="mobile-report-section"><h2>Daily study time</h2><DailyChart daily={data.daily} compact />{!data.summary.session_count && <p className="resource-note">No finished sessions in this range. <Link className="quiz-text-link" href="/focus">Open Focus</Link> to record study time.</p>}</section>
    </>}
    <section className="mobile-report-section" aria-labelledby="analytics-history"><h2 id="analytics-history">Session history</h2>
      <LoadNotice hasData={!!sessions} loading={history.loading} error={history.error} retry={history.retry} />
      {historyStale && <p className="resource-note">Updating history; showing the last loaded sessions.</p>}
      {sessions && data && <>{sessions.sessions.length ? <SessionList sessions={sessions.sessions} timezone={data.timezone} /> : <p className="resource-note">No finished sessions in this range.</p>}<Pagination offset={history.data?.offset ?? offset} total={sessions.total} busy={history.loading} change={setOffset} /></>}
      <p className="resource-note">History shows full session durations. Report totals count only time inside this range.</p>
    </section>
    {data && <>
      <section className="mobile-report-section"><h2>Where time went</h2>{data.subjects.length ? <ul className="mobile-time-list">{data.subjects.map(subject => <li key={subject.subject_id ?? "general"} data-subject={subject.subject_code ?? undefined}><h3><span className="subject-marker" data-color={subject.subject_color_key ?? undefined} aria-hidden="true" />{subject.subject_code ?? "General study"}</h3><TimeBar label="Actual" seconds={subject.duration_seconds} maximum={subjectMaximum} /><p className="resource-note">{subject.session_count} sessions</p></li>)}</ul> : <p className="resource-note">No subject time recorded in this range.</p>}</section>
      <section className="mobile-report-section"><h2>Activity mix</h2>{data.activities.length ? <ul className="mobile-time-list">{data.activities.map(activity => <li key={activity.activity_type}><TimeBar label={activity.activity_type} seconds={activity.duration_seconds} maximum={activityMaximum} /><span className="resource-note">{activity.session_count} sessions</span></li>)}</ul> : <p className="resource-note">No completed activities in this range.</p>}</section>
      <section className="mobile-report-section"><h2>Planned vs actual</h2><TimeBar label="Planned" seconds={data.summary.planned_seconds} maximum={plannedMaximum} planned /><TimeBar label="Actual" seconds={data.summary.total_seconds} maximum={plannedMaximum} />
        {data.subjects.length > 0 && <details><summary>Compare subjects</summary><ul className="mobile-time-list">{data.subjects.map(subject => <li key={subject.subject_id ?? "general"} data-subject={subject.subject_code ?? undefined}><h3>{subject.subject_code ?? "General study"}</h3><TimeBar label="Planned" seconds={subject.planned_seconds} maximum={subjectMaximum} planned /><TimeBar label="Actual" seconds={subject.duration_seconds} maximum={subjectMaximum} /></li>)}</ul></details>}
        <p className="resource-note">Planned event time stays separate from recorded study time. Task estimates are excluded.</p>
      </section>
      <section className="mobile-report-section"><h2>Activity calendar</h2><MobileActivityCalendar daily={data.daily} /></section>
    </>}
    <nav className="learning-progress-links" aria-label="Learning progress"><h2>Learning progress</h2><Link href="/subjects">Lectures</Link><Link href="/quizzes">Quiz results</Link><Link href="/recall">Recall</Link><Link href="/assessments">Assessments</Link></nav>
  </div>;
}
