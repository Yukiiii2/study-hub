"use client";

import Link from "next/link";
import { useCallback, useState } from "react";
import { getAnalytics, getAnalyticsSessions, type AnalyticsRange } from "@/services/analytics";
import { activityTypes } from "@/services/study-plan";
import { LoadNotice, Pagination } from "@/features/quizzes/shared";
import { dateLabel, zonedParts } from "@/features/study-plan/dates";
import { CalendarHeatmap, DailyChart, TimeBar } from "./analytics-charts";
import { rangeError, studyDuration } from "./presentation";
import { SessionList } from "./session-list";
import { useStudyTimeLoad } from "./use-study-time-load";

export function AnalyticsPage() {
  const [range, setRange] = useState<AnalyticsRange>({ period: 7 }), [offset, setOffset] = useState(0);
  const [custom, setCustom] = useState(false), [start, setStart] = useState(""), [end, setEnd] = useState(""), [dateError, setDateError] = useState<string | null>(null);
  const key = JSON.stringify(range);
  const summary = useStudyTimeLoad(useCallback(async (signal) => ({ key, data: await getAnalytics(range, signal) }), [range, key]));
  const history = useStudyTimeLoad(useCallback(async (signal) => ({ key, offset, data: await getAnalyticsSessions(range, offset, signal) }), [range, key, offset]));
  const data = summary.data?.key === key ? summary.data.data : null;
  const sessions = history.data?.key === key && history.data.offset === offset ? history.data.data : null;
  const busy = summary.loading || history.loading;
  const today = summary.data ? zonedParts(new Date(), summary.data.data.timezone).date : "";
  const subjectMaximum = data ? Math.max(0, ...data.subjects.flatMap((subject) => [subject.duration_seconds, subject.planned_seconds])) : 0;
  const activityMaximum = data ? Math.max(0, ...data.activities.map((activity) => activity.duration_seconds)) : 0;
  const plannedMaximum = data ? Math.max(data.summary.total_seconds, data.summary.planned_seconds) : 0;
  const chooseRange = (next: AnalyticsRange) => { setRange(next); setOffset(0); setDateError(null); };
  return <>
    <header className="page-heading resource-heading"><div><h1>Analytics</h1><p>Compare completed study time with your plan.</p></div><div className="resource-actions"><Link href="/focus" className="secondary-button">Open Focus</Link><button type="button" className="secondary-button" disabled={busy} onClick={() => { summary.retry(); history.retry(); }}>Refresh</button></div></header>
    <div className="study-periods ui-toolbar" aria-label="Analytics period">
      {([7, 30, 90] as const).map((period) => <button type="button" key={period} className="secondary-button" aria-pressed={!custom && "period" in range && range.period === period} onClick={() => { setCustom(false); chooseRange({ period }); }}>Last {period} days</button>)}
      <button type="button" className="secondary-button" aria-pressed={custom} onClick={() => { setCustom(true); setStart(data?.start_date ?? ""); setEnd(data?.end_date ?? ""); }}>Custom range</button>
    </div>
    {custom && <form className="resource-filters study-range-form" onSubmit={(event) => { event.preventDefault(); const error = rangeError(start, end, today); setDateError(error); if (!error) chooseRange({ start_date: start, end_date: end }); }}><label>Start date<input type="date" required value={start} max={end || today} onChange={(event) => setStart(event.target.value)} /></label><label>End date<input type="date" required value={end} min={start} max={today} onChange={(event) => setEnd(event.target.value)} /></label><button className="secondary-button" disabled={!today || busy}>Apply range</button><span className="resource-note">Up to 90 days, including both dates.</span></form>}
    {dateError && <p className="auth-error" role="alert">{dateError}</p>}
    <LoadNotice loading={summary.loading} error={summary.error} retry={summary.retry} />
    {data && <div className="analytics-report" aria-busy={summary.loading}>
      <p className="resource-note">{dateLabel(data.start_date, { month: "short", day: "numeric", year: "numeric" })} – {dateLabel(data.end_date, { month: "short", day: "numeric", year: "numeric" })} · {data.timezone}. Only finished sessions count. Times use h:mm:ss.</p>
      <dl className="study-time-metrics ui-metrics analytics-summary"><div><dt>Completed study time</dt><dd>{studyDuration(data.summary.total_seconds)}</dd></div><div><dt>Sessions</dt><dd>{data.summary.session_count}</dd></div><div><dt>Active days</dt><dd>{data.summary.active_days}</dd></div><div><dt>Average session</dt><dd>{studyDuration(data.summary.average_session_seconds)}</dd></div><div><dt>Longest session</dt><dd>{studyDuration(data.summary.longest_session_seconds)}</dd></div></dl>
      {data.summary.session_count === 0 && <p className="resource-note">No completed study sessions in this range. <Link className="quiz-text-link" href="/focus">Start a session in Focus</Link> to record your time.</p>}
      <div className="analytics-layout">
        <section className="study-time-section ui-panel analytics-section-wide" aria-labelledby="analytics-daily"><header className="ui-section-heading"><h2 id="analytics-daily">Daily study time</h2></header><DailyChart daily={data.daily} /></section>
        <section className="study-time-section ui-panel analytics-section-wide analytics-plan" aria-labelledby="analytics-plan"><header className="ui-section-heading"><h2 id="analytics-plan">Planned versus actual</h2></header><TimeBar label="Planned" seconds={data.summary.planned_seconds} maximum={plannedMaximum} planned /><TimeBar label="Actual" seconds={data.summary.total_seconds} maximum={plannedMaximum} /><p className="resource-note">Planned event time and completed session time are independent totals. Unscheduled task estimates are excluded.</p></section>
        <section className="study-time-section ui-panel" aria-labelledby="analytics-subjects"><header className="ui-section-heading"><h2 id="analytics-subjects">Time by subject</h2></header>{data.subjects.length ? <ul className="study-subject-breakdown">{data.subjects.map((subject) => <li key={subject.subject_id ?? "unassigned"}><h3>{subject.subject_id && <span className="subject-marker" data-color={subject.subject_color_key ?? undefined} aria-hidden="true" />}<span>{subject.subject_code ?? "No subject"}{subject.subject_title && <span className="study-subject-title"> — {subject.subject_title}</span>}</span></h3><TimeBar label="Actual" seconds={subject.duration_seconds} maximum={subjectMaximum} /><TimeBar label="Planned" seconds={subject.planned_seconds} maximum={subjectMaximum} planned /><p className="resource-note">{subject.session_count} completed sessions</p></li>)}</ul> : <p className="resource-note">No planned or completed study time by subject in this range.</p>}</section>
        <section className="study-time-section ui-panel" aria-labelledby="analytics-activities"><header className="ui-section-heading"><h2 id="analytics-activities">Time by activity</h2></header><ul className="study-activity-breakdown">{activityTypes.map((type) => { const activity = data.activities.find((item) => item.activity_type === type); return <li key={type}><TimeBar label={type[0].toUpperCase() + type.slice(1)} seconds={activity?.duration_seconds ?? 0} maximum={activityMaximum} /><span className="resource-note">{activity?.session_count ?? 0} sessions</span></li>; })}</ul></section>
        <section className="study-time-section ui-panel analytics-section-wide" aria-labelledby="analytics-calendar"><header className="ui-section-heading"><h2 id="analytics-calendar">Activity calendar</h2></header><CalendarHeatmap daily={data.daily} /></section>
      </div>
    </div>}
    <section className="study-time-section ui-panel analytics-history" aria-labelledby="analytics-history"><header className="ui-section-heading"><h2 id="analytics-history">Session history</h2></header><p className="resource-note">Completed sessions overlapping the selected range. Session durations below show the full recorded session; totals above use only the time inside the range.</p><LoadNotice loading={history.loading} error={history.error} retry={history.retry} />{sessions && data && <>{sessions.sessions.length ? <SessionList sessions={sessions.sessions} timezone={data.timezone} /> : <p className="resource-note">No completed sessions in this range.</p>}<Pagination offset={offset} total={sessions.total} busy={history.loading} change={setOffset} /></>}</section>
  </>;
}
