"use client";

import Link from "next/link";
import { activityTypes } from "@/services/study-plan";
import { LoadNotice, Pagination } from "@/features/quizzes/shared";
import { dateLabel } from "@/features/study-plan/dates";
import { CalendarHeatmap, DailyChart, TimeBar } from "./analytics-charts";
import { studyDuration } from "./presentation";
import { SessionList } from "./session-list";

import type { AnalyticsViewProps } from "./use-analytics-data";
import { AnalyticsControls } from "./analytics-controls";
export function AnalyticsDesktopView(model: AnalyticsViewProps) {
  const { offset, summary, history, data, staleRange, sessions, historyStale, subjectMaximum, activityMaximum, plannedMaximum, setOffset } = model;
  return <><AnalyticsControls model={model} />
    <LoadNotice hasData={summary.data != null} loading={summary.loading} layout="chart" label="Loading study activity..." error={summary.error} retry={summary.retry} />
    <div className="analytics-workspace">{staleRange && <p className="resource-note" role="status">Showing the previous loaded date range until the selected range is available.</p>}{data && <div className="analytics-report" aria-busy={summary.loading}>
      <p className="resource-note">{dateLabel(data.start_date, { month: "short", day: "numeric", year: "numeric" })} – {dateLabel(data.end_date, { month: "short", day: "numeric", year: "numeric" })} · {data.timezone}. Only finished sessions count. Times use h:mm:ss.</p>
      <dl className="study-time-metrics ui-metrics analytics-summary"><div><dt>Completed study time</dt><dd>{studyDuration(data.summary.total_seconds)}</dd></div><div><dt>Sessions</dt><dd>{data.summary.session_count}</dd></div><div><dt>Active days</dt><dd>{data.summary.active_days}</dd></div><div><dt>Average session</dt><dd>{studyDuration(data.summary.average_session_seconds)}</dd></div><div><dt>Longest session</dt><dd>{studyDuration(data.summary.longest_session_seconds)}</dd></div></dl>
      {data.summary.session_count === 0 && <div className="resource-empty"><h2>No completed sessions in this range</h2><p><Link className="quiz-text-link" href="/focus">Start a session in Focus</Link> to record your time.</p></div>}
      <div className="analytics-layout">
        <section className="study-time-section ui-panel analytics-daily" aria-labelledby="analytics-daily"><header className="ui-section-heading"><h2 id="analytics-daily">Daily study time</h2></header><DailyChart daily={data.daily} /></section>
        <section className="study-time-section ui-panel analytics-subjects" aria-labelledby="analytics-subjects"><header className="ui-section-heading"><h2 id="analytics-subjects">Time by subject</h2></header>{data.subjects.length ? <ul className="study-subject-breakdown">{data.subjects.map((subject) => <li key={subject.subject_id ?? "unassigned"} data-subject={subject.subject_code ?? undefined}><h3>{subject.subject_id && <span className="subject-marker" data-color={subject.subject_color_key ?? undefined} aria-hidden="true" />}<span>{subject.subject_code ?? "No subject"}{subject.subject_title && <span className="study-subject-title"> — {subject.subject_title}</span>}</span></h3><TimeBar label="Actual" seconds={subject.duration_seconds} maximum={subjectMaximum} /><TimeBar label="Planned" seconds={subject.planned_seconds} maximum={subjectMaximum} planned /><p className="resource-note">{subject.session_count} completed sessions</p></li>)}</ul> : <p className="resource-note">No planned or completed study time by subject in this range.</p>}</section>
        <section className="study-time-section ui-panel analytics-activities" aria-labelledby="analytics-activities"><header className="ui-section-heading"><h2 id="analytics-activities">Time by activity</h2></header><ul className="study-activity-breakdown">{activityTypes.map((type) => { const activity = data.activities.find((item) => item.activity_type === type); return <li key={type}><TimeBar label={type[0].toUpperCase() + type.slice(1)} seconds={activity?.duration_seconds ?? 0} maximum={activityMaximum} /><span className="resource-note">{activity?.session_count ?? 0} sessions</span></li>; })}</ul></section>
        <section className="study-time-section ui-panel analytics-plan" aria-labelledby="analytics-plan"><header className="ui-section-heading"><h2 id="analytics-plan">Planned versus actual</h2></header><TimeBar label="Planned" seconds={data.summary.planned_seconds} maximum={plannedMaximum} planned /><TimeBar label="Actual" seconds={data.summary.total_seconds} maximum={plannedMaximum} /><p className="resource-note">Planned event time and completed session time are independent totals. Unscheduled task estimates are excluded.</p></section>
        <section className="study-time-section ui-panel analytics-section-wide" aria-labelledby="analytics-calendar"><header className="ui-section-heading"><h2 id="analytics-calendar">Activity calendar</h2></header><CalendarHeatmap daily={data.daily} /></section>
      </div>
    </div>}
    <section className="study-time-section ui-panel analytics-history" aria-labelledby="analytics-history"><header className="ui-section-heading"><h2 id="analytics-history">Session history</h2></header><p className="resource-note">Completed sessions overlapping the selected range. Session durations below show the full recorded session; totals above use only the time inside the range.</p><LoadNotice hasData={history.data != null} loading={history.loading} error={history.error} retry={history.retry} />{historyStale && <p className="resource-note">Showing the last loaded session page until the selected range and page are ready.</p>}{sessions && data && <>{sessions.sessions.length ? <SessionList sessions={sessions.sessions} timezone={data.timezone} /> : <p className="resource-note">No completed sessions in this range.</p>}<Pagination offset={history.data?.offset ?? offset} total={sessions.total} busy={history.loading} change={setOffset} /></>}</section>
    </div><nav className="learning-progress-links" aria-label="Learning progress"><h2>Learning progress</h2><Link href="/subjects">Lectures & curriculum</Link><Link href="/quizzes">Quiz results</Link><Link href="/recall">Recall queue</Link><Link href="/assessments">Assessment coverage</Link></nav>
  </>;
}
