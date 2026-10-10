"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError } from "@/services/api";
import { getFocus, startFocus, studyTimeError, type FocusData } from "@/services/analytics";
import { getSubjects, getSubjectTopics } from "@/services/subjects";
import { activityTypes, eventActivity, getEvent, getEvents, stopSession, type ActivityType, type StudyEvent } from "@/services/study-plan";
import { LoadNotice } from "@/features/quizzes/shared";
import { useStudyTimeLoad } from "@/features/analytics/use-study-time-load";
import { dateLabel, zonedParts } from "@/features/study-plan/dates";
import { eventOverlapsFocusDates, focusEventWindow } from "./event-window";
import { elapsedSeconds, studyDuration, type ClockAnchor } from "@/features/analytics/presentation";
import { SessionList } from "@/features/analytics/session-list";

type Props = { subjectId: string; topicId: string; eventId: string; occurrenceDate: string };
type Snapshot = { data: FocusData; anchor: ClockAnchor };
const eventKey = (event: StudyEvent) => `${event.id}/${event.occurrence_date ?? ""}`;

export function FocusPage({ subjectId, topicId, eventId, occurrenceDate }: Props) {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [refreshing, setRefreshing] = useState(true), [loadError, setLoadError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null), [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false), busyRef = useRef(false);
  const alive = useRef(false), refreshAbort = useRef<AbortController | null>(null);
  const [subject, setSubject] = useState(subjectId), [topic, setTopic] = useState(topicId);
  const [activity, setActivity] = useState<ActivityType>("general");
  const [selectedEvent, setSelectedEvent] = useState(eventId ? `${eventId}/${occurrenceDate}` : "");
  const [occurrence, setOccurrence] = useState(occurrenceDate);
  const [, setTick] = useState(0);
  const subjects = useStudyTimeLoad(useCallback((signal) => getSubjects(signal), []));
  const active = snapshot?.data.active_session;
  const topicSubject = active ? active.subject_id ?? "" : subject;
  const topics = useStudyTimeLoad(useCallback((signal) => topicSubject ? getSubjectTopics(topicSubject, signal) : Promise.resolve([]), [topicSubject]));

  const refresh = useCallback(async () => {
    refreshAbort.current?.abort();
    const controller = new AbortController(); refreshAbort.current = controller;
    setRefreshing(true); setLoadError(null);
    try {
      const data = await getFocus(controller.signal);
      if (!controller.signal.aborted && alive.current) setSnapshot({ data, anchor: { serverTime: Date.parse(data.server_now), monotonicTime: performance.now() } });
    } catch (error) { if (!controller.signal.aborted && alive.current) setLoadError(studyTimeError(error)); }
    finally { if (!controller.signal.aborted && alive.current) setRefreshing(false); }
  }, []);

  useEffect(() => {
    alive.current = true; void refresh();
    const visible = () => { if (document.visibilityState === "visible" && !busyRef.current) void refresh(); };
    document.addEventListener("visibilitychange", visible);
    return () => { alive.current = false; refreshAbort.current?.abort(); document.removeEventListener("visibilitychange", visible); };
  }, [refresh]);
  useEffect(() => {
    if (!active) return;
    const timer = window.setInterval(() => setTick((value) => value + 1), 1000);
    return () => window.clearInterval(timer);
  }, [active?.id]);
  const timezone = snapshot?.data.timezone;
  const today = snapshot ? zonedParts(snapshot.data.server_now, snapshot.data.timezone).date : "";
  const events = useStudyTimeLoad(useCallback(async (signal) => {
    if (!timezone || !today) return [];
    const window = focusEventWindow(today);
    const values = (await getEvents(window.startAt, window.endAt, signal)).filter((value) => eventOverlapsFocusDates(value, today, window.endDate, timezone));
    if (eventId && !values.some((event) => event.id === eventId && (event.occurrence_date ?? "") === occurrenceDate)) {
      const event = await getEvent(eventId, signal);
      // The backend validates a requested recurrence date, including occurrence edits/deletions.
      values.unshift({ ...event, occurrence_date: occurrenceDate || null });
    }
    return values;
  }, [timezone, today, eventId, occurrenceDate]));
  const event = events.data?.find((value) => eventKey(value) === selectedEvent);
  const currentTopics = topics.data?.filter((value) => value.subject_id === topicSubject) ?? [];
  const validSubject = !subject || subjects.data?.some((value) => value.id === subject);
  const validTopic = !topic || currentTopics.some((value) => value.id === topic);
  const validEvent = !selectedEvent || !!event;
  const needsOccurrence = !!event?.recurrence_rule;
  const elapsed = active && snapshot ? elapsedSeconds(active.started_at, snapshot.anchor, performance.now()) : 0;

  async function act(stop: boolean) {
    if (busyRef.current || refreshing || !snapshot) return;
    if (!stop && (!validEvent || (!event && (!validSubject || !validTopic)) || (needsOccurrence && !occurrence))) {
      setActionError("Choose an available event or matching subject and topic before starting."); return;
    }
    busyRef.current = true; setBusy(true); setActionError(null); setNotice(null);
    try {
      if (stop && active) {
        await stopSession(active.id);
        if (alive.current) {
          setSnapshot((previous) => previous ? { ...previous, data: { ...previous.data, active_session: null } } : previous);
          setNotice("Session finished. Your study time has been saved.");
        }
      } else if (!stop && !active) {
        const started = await startFocus({ activity_type: activity, ...(event ? { study_event_id: event.id, ...(needsOccurrence ? { occurrence_date: occurrence } : {}) } : { ...(subject ? { subject_id: subject } : {}), ...(topic ? { topic_id: topic } : {}) }) });
        if (alive.current) setSnapshot((previous) => previous ? { data: { ...previous.data, active_session: started }, anchor: { serverTime: Date.parse(started.started_at), monotonicTime: performance.now() } } : previous);
      }
      if (alive.current) await refresh();
    } catch (error) {
      if (alive.current) {
        setActionError(error instanceof ApiError && error.status === 409 ? "Another session is already active. Restoring the saved session." : `${studyTimeError(error)} Refresh to check the saved state, or retry.`);
        // A failed response can follow a committed operation. Restore server truth.
        await refresh();
      }
    } finally { busyRef.current = false; if (alive.current) setBusy(false); }
  }

  const activeSubject = subjects.data?.find((value) => value.id === active?.subject_id);
  const activeTopic = currentTopics.find((value) => value.id === active?.topic_id);
  return <>
    <header className="page-heading resource-heading"><div><h1>Focus</h1><p>Start a study session and keep your actual study time.</p></div><button type="button" className="secondary-button" disabled={busy || refreshing} onClick={() => void refresh()}>{refreshing ? "Refreshing…" : "Refresh"}</button></header>
    <LoadNotice loading={!snapshot && refreshing} error={loadError} retry={() => void refresh()} />
    {loadError && snapshot && <p className="resource-note">Showing the last loaded totals. Use Refresh to check the current session and totals.</p>}
    {actionError && <p className="auth-error" role="alert">{actionError}</p>}
    {notice && <p className="study-time-notice" role="status">{notice}</p>}
    {snapshot && <div className="focus-layout">
      <div className="focus-main">
      <section className="focus-session ui-panel" aria-labelledby="focus-session-title" aria-busy={busy || refreshing}>
        <header className="ui-section-heading"><h2 id="focus-session-title">{active ? "Session in progress" : "Start a session"}</h2></header>
        {active ? <div className="focus-timer-stage">
          <p className="resource-note">{activeSubject?.code ?? (active.subject_id ? "Subject selected" : "No subject")}{activeTopic ? ` — ${activeTopic.title}` : ""} · {active.activity_type}{active.study_event_id && " · Linked to a planned event"}</p>
          <div className="focus-timer" role="timer" aria-label={`Elapsed study time ${studyDuration(elapsed)}`}>{studyDuration(elapsed)}</div>
          <p className="resource-note">Started <time dateTime={active.started_at}>{new Intl.DateTimeFormat("en", { timeZone: snapshot.data.timezone, month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).format(new Date(active.started_at))}</time>. Finish the session to save its recorded duration.</p>
          <button type="button" className="primary-button" disabled={busy || refreshing} onClick={() => void act(true)}>{busy ? "Finishing…" : "Finish session"}</button>
        </div> : <form className="quiz-builder-form focus-session-form" onSubmit={(value) => { value.preventDefault(); void act(false); }}>
          <fieldset className="planner-form-grid" disabled={busy || refreshing}>
            <label className="planner-wide">Planned event (optional)<select value={selectedEvent} disabled={events.loading} onChange={(value) => {
              setSelectedEvent(value.target.value); const next = events.data?.find((item) => eventKey(item) === value.target.value);
              setOccurrence(next?.occurrence_date ?? ""); if (next) setActivity(eventActivity(next));
            }}><option value="">Independent study</option>{selectedEvent && !event && <option value={selectedEvent}>Selected event unavailable</option>}{events.data?.map((value) => <option key={eventKey(value)} value={eventKey(value)}>{value.title} — {dateLabel(zonedParts(value.start_at, snapshot.data.timezone).date)} {zonedParts(value.start_at, snapshot.data.timezone).time}</option>)}</select></label>
            {needsOccurrence && <label>Recurring occurrence date<input type="date" required value={occurrence} onChange={(value) => setOccurrence(value.target.value)} /></label>}
            {event ? <p className="resource-note planner-wide">Subject and topic come from the saved event. Finishing a session does not change its planned status.</p> : <>
              <label>Subject (optional)<select value={subject} disabled={subjects.loading || !!subjects.error} onChange={(value) => { setSubject(value.target.value); setTopic(""); }}><option value="">No subject</option>{subject && !validSubject && <option value={subject}>Selected subject unavailable</option>}{subjects.data?.map((value) => <option key={value.id} value={value.id}>{value.code} — {value.name}</option>)}</select></label>
              <label>Topic (optional)<select value={topic} disabled={!subject || topics.loading || !!topics.error} onChange={(value) => setTopic(value.target.value)}><option value="">No topic</option>{topic && !validTopic && <option value={topic}>Selected topic unavailable</option>}{currentTopics.map((value) => <option key={value.id} value={value.id}>{value.title}</option>)}</select></label>
            </>}
            <label>Activity<select value={activity} onChange={(value) => setActivity(value.target.value as ActivityType)}>{activityTypes.map((value) => <option value={value} key={value}>{value[0].toUpperCase() + value.slice(1)}</option>)}</select></label>
          </fieldset>
          <LoadNotice loading={false} error={events.error} retry={events.retry} />
          {!event && <><LoadNotice loading={false} error={subjects.error} retry={subjects.retry} /><LoadNotice loading={false} error={topics.error} retry={topics.retry} /></>}
          {((!events.loading && !validEvent) || (!event && !subjects.loading && !topics.loading && (!validSubject || !validTopic))) && <p className="auth-error" role="alert">Choose an available event or matching subject and topic before starting.</p>}
          <button className="primary-button focus-start" disabled={busy || refreshing || !validEvent || (!event && (!validSubject || !validTopic || (subject !== "" && topics.loading))) || (needsOccurrence && !occurrence)}>{busy ? "Starting…" : "Start session"}</button>
        </form>}
      </section>
      </div>
      <div className="focus-sidebar">
        <section className="study-time-section ui-panel focus-today" aria-labelledby="focus-today"><div className="section-heading ui-section-heading"><h2 id="focus-today">Today</h2><span>{snapshot.data.timezone}</span></div><dl className="study-time-metrics ui-metrics"><div><dt>Completed study time</dt><dd>{studyDuration(snapshot.data.today_seconds)}</dd></div><div><dt>Completed sessions</dt><dd>{snapshot.data.today_session_count}</dd></div></dl><p className="resource-note">The active session is included after you finish. Times use h:mm:ss.</p></section>
        <section className="study-time-section ui-panel focus-recent" aria-labelledby="focus-recent"><div className="section-heading ui-section-heading"><h2 id="focus-recent">Recent sessions</h2><Link className="quiz-text-link" href="/analytics">View Analytics</Link></div>{snapshot.data.recent_sessions.length ? <SessionList sessions={snapshot.data.recent_sessions} timezone={snapshot.data.timezone} /> : <p className="resource-note">No completed sessions yet. Start a session to record your study time.</p>}</section>
        {!!subjects.data?.length && <section className="study-time-section ui-panel focus-subjects" aria-labelledby="focus-subjects"><header className="ui-section-heading"><h2 id="focus-subjects">Subjects</h2><Link className="quiz-text-link" href="/subjects">All subjects</Link></header><nav className="focus-subject-links" aria-label="Subject shortcuts">{subjects.data.map((value) => <Link className="secondary-button focus-subject-link" href={`/subjects/${encodeURIComponent(value.id)}`} key={value.id}><span className="subject-marker" data-color={value.color_key ?? undefined} aria-hidden="true" />{value.code}</Link>)}</nav></section>}
      </div>
    </div>}
  </>;
}
