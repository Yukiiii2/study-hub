"use client";

import { useEffect, useState } from "react";
import { getSubjects, type Subject } from "@/services/subjects";
import { getEvent, getEvents, getPlannerContext, getTasks, plannerError, startSession, stopSession, updateEvent, updateTask, type PlannerContext, type StudyEvent, type StudyTask } from "@/services/study-plan";
import { calendarDays, dateAdd, dateLabel, localToInstant, zonedParts } from "./dates";
import { EventDialog, TaskDialog } from "./planner-dialogs";

type DialogState = { kind: "event"; event?: StudyEvent; task?: StudyTask; date: string; time?: string } | { kind: "task"; task?: StudyTask };
type Tab = "calendar" | "today" | "tasks";
const weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const hours = Array.from({ length: 12 }, (_, index) => index * 2);

export function StudyPlanner() {
  const [context, setContext] = useState<PlannerContext | null>(null);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [tasks, setTasks] = useState<StudyTask[]>([]);
  const [events, setEvents] = useState<StudyEvent[]>([]);
  const [tab, setTab] = useState<Tab>("calendar");
  const [view, setView] = useState<"month" | "week">("month");
  const [anchor, setAnchor] = useState("");
  const [revision, setRevision] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [eventError, setEventError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [eventsLoading, setEventsLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [dialog, setDialog] = useState<DialogState | null>(null);
  const refresh = () => setRevision((value) => value + 1);
  const saved = () => { setNotice("Planner updated."); refresh(); };

  useEffect(() => {
    const controller = new AbortController(); setLoading(true); setError(null);
    void Promise.all([getPlannerContext(controller.signal), getSubjects(controller.signal), getTasks(controller.signal)]).then(([context, subjects, tasks]) => {
      if (controller.signal.aborted) return;
      setContext(context); setSubjects(subjects); setTasks(tasks);
      setAnchor((current) => current || zonedParts(new Date(), context.timezone).date);
    }).catch((error) => { if (!controller.signal.aborted) setError(plannerError(error)); }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [revision]);

  const timezone = context?.timezone ?? "UTC";
  const today = zonedParts(new Date(), timezone).date;
  const days = anchor ? calendarDays(anchor, view) : [];
  const start = tab === "today" ? today : days[0];
  const end = tab === "today" ? dateAdd(today, 1) : days.length ? dateAdd(days[days.length - 1], 1) : "";

  useEffect(() => {
    if (!context || !start || !end || tab === "tasks") return;
    const controller = new AbortController(); setEventsLoading(true); setEventError(null);
    void (async () => {
      const events = await getEvents(localToInstant(start, "00:00", timezone), localToInstant(end, "00:00", timezone), controller.signal);
      if (!controller.signal.aborted) setEvents(events);
    })().catch((error) => { if (!controller.signal.aborted) setEventError(plannerError(error)); }).finally(() => { if (!controller.signal.aborted) setEventsLoading(false); });
    return () => controller.abort();
  }, [context, start, end, timezone, tab, revision]);

  const subjectFor = (id: string | null) => subjects.find((subject) => subject.id === id);
  function eventsOn(date: string) {
    return events.filter((event) => {
      const start = zonedParts(event.start_at, timezone), end = zonedParts(event.end_at, timezone);
      return start.date <= date && (end.date > date || (end.date === date && end.time !== "00:00"));
    });
  }
  function eventButton(event: StudyEvent, compact = false) {
    const subject = subjectFor(event.subject_id);
    const start = zonedParts(event.start_at, timezone), end = zonedParts(event.end_at, timezone);
    return <button type="button" key={`${event.id}/${event.occurrence_date ?? "one"}`} disabled={busy || loading} className={`planner-event${compact ? " planner-event-compact" : ""}`} data-status={event.status} onClick={() => setDialog({ kind: "event", event, date: start.date })}>
      <span className="subject-marker" data-color={subject?.color_key ?? undefined} aria-hidden="true" />
      <span className="planner-event-copy"><strong>{event.title}</strong><span>{start.time}{!compact && `–${end.time}`} {subject?.code ?? "General"}{!compact && ` · ${event.event_type === "general" ? "study" : event.event_type}`}{event.is_recurring && " · repeats"}</span>{event.status !== "scheduled" && <span className="planner-status">{event.status}</span>}</span>
    </button>;
  }
  async function beginSession(event?: StudyEvent) {
    const session = await startSession(event);
    setContext((current) => current ? { ...current, active_session: session } : current);
    setNotice("Study session started. Stop it when you finish.");
  }
  async function perform(action: () => Promise<void>) {
    setBusy(true); setActionError(null); setNotice(null);
    try { await action(); } catch (error) { setActionError(plannerError(error)); } finally { setBusy(false); }
  }
  function move(direction: number) {
    if (view === "week") setAnchor(dateAdd(anchor, direction * 7));
    else { const date = new Date(`${anchor.slice(0, 7)}-01T12:00:00Z`); date.setUTCMonth(date.getUTCMonth() + direction); setAnchor(date.toISOString().slice(0, 10)); }
  }

  return <section className="study-planner" aria-labelledby="planner-title">
    <header className="page-heading planner-heading"><div><h1 id="planner-title">Study Plan</h1><p>Plan your review. Record the time you actually study.</p></div><button type="button" className="primary-button" disabled={!context || loading} onClick={() => setDialog(tab === "tasks" ? { kind: "task" } : { kind: "event", date: today })}>{tab === "tasks" ? "New task" : "New event"}</button></header>
    <nav className="planner-tabs" aria-label="Study planner views">{(["calendar", "today", "tasks"] as Tab[]).map((value) => <button type="button" key={value} aria-current={tab === value ? "page" : undefined} onClick={() => setTab(value)}>{value[0].toUpperCase() + value.slice(1)}</button>)}</nav>
    {loading && <p role="status" className="planner-note">Loading planner…</p>}
    {error && <div className="curriculum-state"><p role="alert" className="auth-error">{error}</p><button type="button" className="secondary-button" onClick={refresh}>Refresh planner</button></div>}
    {context && !error && <>
      <section className="planner-session" aria-label="Actual study time"><div><strong>{context.active_session ? "Study session in progress" : "Record actual study time"}</strong><p>{context.active_session ? `Started ${dateLabel(zonedParts(context.active_session.started_at, timezone).date)} at ${zonedParts(context.active_session.started_at, timezone).time} (${timezone}).` : "Start a session here or from a calendar event. Planned time stays separate."}</p></div><button type="button" className="secondary-button" disabled={busy || loading} onClick={() => void perform(async () => {
        if (context.active_session) { const finished = await stopSession(context.active_session.id); setNotice(`Session stopped. ${Math.floor((finished.duration_seconds ?? 0) / 60)} minutes recorded.`); setContext((current) => current ? { ...current, active_session: null } : current); }
        else await beginSession();
      })}>{busy ? "Saving…" : context.active_session ? "Stop session" : "Start session"}</button></section>
      {actionError && <div className="planner-action-error"><p role="alert" className="auth-error">{actionError}</p><button type="button" className="secondary-button" disabled={busy} onClick={refresh}>Refresh planner</button></div>}
      {notice && <p role="status" className="planner-notice">{notice}</p>}
      {tab === "tasks" ? <section aria-labelledby="task-list-title"><div className="section-heading"><h2 id="task-list-title">Study tasks</h2><span>{tasks.length} {tasks.length === 1 ? "task" : "tasks"}</span></div>
        {!tasks.length ? <div className="curriculum-state"><h3>No study tasks yet</h3><p>Add work to organize before choosing a study time.</p></div> : <ul className="planner-task-list">{tasks.map((task) => {
          const subject = subjectFor(task.subject_id), due = task.due_at ? zonedParts(task.due_at, timezone) : null;
          return <li className="planner-task" key={task.id}><span className="subject-marker" data-color={subject?.color_key ?? undefined} aria-hidden="true" /><div className="planner-task-copy"><h3>{task.title}</h3><p>{subject?.code ?? "General"} · {task.task_type} · {task.status}{task.estimated_minutes ? ` · ${task.estimated_minutes} min planned` : ""}</p>{due && <p>Due {dateLabel(due.date)} at {due.time}{task.status !== "completed" && task.status !== "cancelled" && new Date(task.due_at!) < new Date() ? " · overdue" : ""}</p>}</div><div className="planner-task-actions">
            <button type="button" className="secondary-button" disabled={busy || loading} onClick={() => setDialog({ kind: "task", task })}>Edit</button>
            {task.status === "pending" && <button type="button" className="secondary-button" disabled={busy || loading} onClick={() => setDialog({ kind: "event", task, date: today })}>Schedule</button>}
            {task.scheduled_event_id && <button type="button" className="secondary-button" disabled={busy || loading} onClick={() => void perform(async () => { const event = await getEvent(task.scheduled_event_id!); setDialog({ kind: "event", event, date: zonedParts(event.start_at, event.timezone).date }); })}>Linked event</button>}
            {task.status !== "completed" && task.status !== "cancelled" && <button type="button" className="secondary-button" disabled={busy || loading} onClick={() => void perform(async () => { await updateTask(task.id, { status: "completed" }); saved(); })}>Complete</button>}
          </div></li>;
        })}</ul>}
      </section> : <>
        <div className="planner-calendar-toolbar"><div className="planner-period-controls">{tab === "calendar" && <><button type="button" className="secondary-button" aria-label={`Previous ${view}`} onClick={() => move(-1)}>‹</button><button type="button" className="secondary-button" onClick={() => setAnchor(today)}>Today</button><button type="button" className="secondary-button" aria-label={`Next ${view}`} onClick={() => move(1)}>›</button></>}<h2>{tab === "today" ? dateLabel(today, { weekday: "long", month: "long", day: "numeric" }) : view === "month" ? dateLabel(anchor, { month: "long", year: "numeric" }) : `${dateLabel(days[0])} – ${dateLabel(days[6], { month: "short", day: "numeric", year: "numeric" })}`}</h2></div>{tab === "calendar" && <div className="planner-view-controls" aria-label="Calendar layout">{(["month", "week"] as const).map((value) => <button type="button" key={value} className="secondary-button" aria-pressed={view === value} onClick={() => setView(value)}>{value === "month" ? "Month" : "Week"}</button>)}</div>}</div>
        <p className="planner-timezone">Times shown in {timezone}. Select a date or time to add an event.</p>
        {eventError ? <div className="curriculum-state"><p className="auth-error" role="alert">{eventError}</p><button type="button" className="secondary-button" onClick={refresh}>Try again</button></div> : eventsLoading ? <p className="curriculum-loading" role="status">Loading study events…</p> : tab === "today" ? <div className="planner-agenda">{eventsOn(today).length ? eventsOn(today).map((event) => <div className="planner-today-row" key={`${event.id}/${event.occurrence_date ?? "one"}`}>{eventButton(event)}{event.status === "scheduled" && <button type="button" className="secondary-button" aria-label={`Complete ${event.title}`} disabled={busy || loading} onClick={() => void perform(async () => { await updateEvent(event, { status: "completed" }); saved(); })}>Complete</button>}</div>) : <div className="curriculum-state"><h3>No study events today</h3><p>Add a study event or schedule a task when you are ready.</p><button className="secondary-button" onClick={() => setDialog({ kind: "event", date: today })}>Add today&apos;s event</button></div>}</div> : <>
          {events.length === 0 && <p className="planner-note">No events in this period. Select a date or time to plan your review.</p>}
          <div className={`planner-calendar planner-${view}`} aria-label={`${view} calendar`}>
            {view === "month" ? <><div className="planner-week-header">{weekdays.map((day) => <span key={day}>{day}</span>)}</div><div className="planner-month-grid">{days.map((date) => <section className="planner-month-day" data-outside={date.slice(0, 7) !== anchor.slice(0, 7)} data-today={date === today} key={date} aria-label={dateLabel(date, { weekday: "long", month: "long", day: "numeric" })}><button type="button" className="planner-date-button" aria-label={`Add event on ${dateLabel(date)}`} onClick={() => setDialog({ kind: "event", date })}>{Number(date.slice(-2))}</button>{eventsOn(date).map((event) => eventButton(event, true))}</section>)}</div></> : <div className="planner-week-grid"><div className="planner-week-times" aria-hidden="true"><div className="planner-week-day-header" style={{ gridColumn: 1, gridRow: 1 }}>Time</div>{hours.map((hour, hourIndex) => <div className="planner-hour" style={{ gridColumn: 1, gridRow: hourIndex + 2 }} key={hour}>{`${String(hour).padStart(2, "0")}:00`}</div>)}</div>{days.map((date, dayIndex) => <section className="planner-week-column" key={date} data-today={date === today} aria-label={dateLabel(date, { weekday: "long", month: "long", day: "numeric" })}><button className="planner-week-day-header" style={{ gridColumn: dayIndex + 2, gridRow: 1 }} onClick={() => setDialog({ kind: "event", date })}>{dateLabel(date, { weekday: "short", day: "numeric" })}</button>{hours.map((hour, hourIndex) => <div className="planner-time-cell" style={{ gridColumn: dayIndex + 2, gridRow: hourIndex + 2 }} key={hour}><button className="planner-time-add" aria-label={`Add event on ${dateLabel(date)} at ${String(hour).padStart(2, "0")}:00`} onClick={() => setDialog({ kind: "event", date, time: `${String(hour).padStart(2, "0")}:00` })}><span aria-hidden="true">+</span></button>{eventsOn(date).filter((event) => { const start = zonedParts(event.start_at, timezone); const startHour = start.date < date ? 0 : Number(start.time.slice(0, 2)); return startHour >= hour && startHour < hour + 2; }).map((event) => eventButton(event, true))}</div>)}</section>)}</div>}
          </div>
          <div className="planner-mobile-agenda" aria-label="Calendar agenda">{days.map((date) => <section className="planner-agenda-day" key={date}><div className="planner-agenda-heading"><h3>{dateLabel(date, { weekday: "short", month: "short", day: "numeric" })}{date === today ? " · Today" : ""}</h3><button className="secondary-button" aria-label={`Add event on ${dateLabel(date)}`} onClick={() => setDialog({ kind: "event", date })}>Add event</button></div>{eventsOn(date).length ? eventsOn(date).map((event) => eventButton(event)) : <p className="planner-note">No events</p>}</section>)}</div>
        </>}
      </>}
      {dialog?.kind === "event" && <EventDialog {...dialog} subjects={subjects} timezone={timezone} saved={saved} close={() => setDialog(null)} beginSession={beginSession} />}
      {dialog?.kind === "task" && <TaskDialog {...dialog} subjects={subjects} timezone={timezone} saved={saved} close={() => setDialog(null)} />}
    </>}
  </section>;
}
