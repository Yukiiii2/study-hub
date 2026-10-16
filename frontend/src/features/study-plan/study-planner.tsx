"use client";

import { useEffect, useRef, useState } from "react";
import { getSubjects, type Subject } from "@/services/subjects";
import { getEvent, getEvents, getPlannerContext, getTasks, plannerError, startSession, stopSession, updateEvent, updateTask, type PlannerContext, type StudyEvent, type StudyTask } from "@/services/study-plan";
import { calendarDays, compactMonthDays, dateAdd, dateLabel, localToInstant, zonedParts } from "./dates";
import { ResponsiveView } from "@/components/responsive-view";
import { PlanDesktopView, PlanDesktopCalendar } from "./plan-desktop-view";
import { PlanMobileView, PlanMobileCalendar } from "./plan-mobile-view";
import { EventDialog, TaskDialog } from "./planner-dialogs";
import { PendingLabel, ContentSkeleton, LoadingNotice, StatusBadge } from "@/components/study-ui";
import { PageHeader } from "@/components/page-header";
import { SummaryMetric } from "@/components/summary-metric";
import { InterfaceIcon } from "@/components/interface-icon";

type DialogState = { kind: "event"; event?: StudyEvent; task?: StudyTask; date: string; time?: string } | { kind: "task"; task?: StudyTask };
type Tab = "calendar" | "today" | "tasks";
type LoadedPeriod = { key: string; days: string[]; view: "month" | "week"; anchor: string; tab: Tab; today: string };

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
  const [loadedPeriod, setLoadedPeriod] = useState<LoadedPeriod | null>(null);
  const [tasksKnown, setTasksKnown] = useState(false);
  const [subjectsKnown, setSubjectsKnown] = useState(false);
  const [selectedDate, setSelectedDate] = useState("");
  const actionLock = useRef(false);
  useEffect(() => { if (window.matchMedia("(min-width: 960px) and (max-width: 1199px) and (orientation: landscape)").matches) setView("week"); }, []);
  const refresh = () => setRevision((value) => value + 1);
  const saved = () => { setNotice("Planner updated."); refresh(); };

  useEffect(() => {
    const controller = new AbortController(); setLoading(true); setError(null);
    void Promise.allSettled([
      getPlannerContext(controller.signal).then((value) => { if (!controller.signal.aborted) { setContext(value); setAnchor((current) => current || zonedParts(new Date(), value.timezone).date); } }),
      getSubjects(controller.signal).then((value) => { if (!controller.signal.aborted) { setSubjects(value); setSubjectsKnown(true); } }),
      getTasks(controller.signal).then((value) => { if (!controller.signal.aborted) { setTasks(value); setTasksKnown(true); } }),
    ]).then(([context, subjects, tasks]) => {
      if (controller.signal.aborted) return;
      const failures = [context, subjects, tasks].flatMap((result, index) => result.status === "rejected" ? [`${["Planner context", "Subjects", "Tasks"][index]}: ${plannerError(result.reason)}`] : []);
      setError(failures.length ? failures.join(" ") : null);
    }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [revision]);

  const timezone = context?.timezone ?? "UTC";
  const today = zonedParts(new Date(), timezone).date;
  const days = anchor ? calendarDays(anchor, view) : [];
  // Include the preceding Sunday for the compact month, without changing desktop Monday-first cells.
  const start = tab === "today" ? today : days.length ? view === "month" ? dateAdd(days[0], -1) : days[0] : "";
  const end = tab === "today" ? dateAdd(today, 1) : days.length ? dateAdd(days[days.length - 1], 1) : "";
  const rangeKey = JSON.stringify([start, end, timezone, tab, view]);
  const samePeriod = loadedPeriod?.key === rangeKey;
  const eventPending = eventsLoading || (!eventError && !samePeriod);
  const shownDays = loadedPeriod?.days ?? days, shownView = loadedPeriod?.view ?? view;
  const shownAnchor = loadedPeriod?.anchor ?? anchor, shownTab = loadedPeriod?.tab ?? tab, shownToday = loadedPeriod?.today ?? today;
  const compactDays = shownAnchor && shownDays.length ? shownView === "month" ? compactMonthDays(shownAnchor) : shownDays : [];
  const defaultSelection = shownView === "month" ? today.slice(0, 7) === shownAnchor.slice(0, 7) ? today : `${shownAnchor.slice(0, 7)}-01` : compactDays.includes(today) ? today : compactDays[0];
  const selectedDay = selectedDate && compactDays.includes(selectedDate) ? selectedDate : defaultSelection;
  useEffect(() => {
    if (!loadedPeriod) return;
    setSelectedDate(current => current && (shownView === "month" ? current.slice(0, 7) === shownAnchor.slice(0, 7) : compactDays.includes(current)) ? current : defaultSelection);
  }, [loadedPeriod?.anchor, loadedPeriod?.view, loadedPeriod?.days[0]]);

  useEffect(() => {
    if (!context || !start || !end || tab === "tasks") return;
    const controller = new AbortController(); setEventsLoading(true); setEventError(null);
    void (async () => {
      const events = await getEvents(localToInstant(start, "00:00", timezone), localToInstant(end, "00:00", timezone), controller.signal);
      if (!controller.signal.aborted) { setEvents(events); setLoadedPeriod({ key: rangeKey, days, view, anchor, tab, today }); }
    })().catch((error) => { if (!controller.signal.aborted) setEventError(plannerError(error)); }).finally(() => { if (!controller.signal.aborted) setEventsLoading(false); });
    return () => controller.abort();
  }, [context, start, end, timezone, tab, revision, rangeKey]);

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
      <span className="planner-event-copy"><strong>{event.title}</strong><span>{start.time}{!compact && `–${end.time}`} {subject?.code ?? "General"}{!compact && ` · ${event.event_type === "general" ? "study" : event.event_type}`}{event.is_recurring && " · repeats"}</span>{event.status !== "scheduled" && <StatusBadge tone={event.status === "completed" ? "success" : "neutral"}>{event.status}</StatusBadge>}</span>
    </button>;
  }
  async function beginSession(event?: StudyEvent) {
    const session = await startSession(event);
    setContext((current) => current ? { ...current, active_session: session } : current);
    setNotice("Study session started. Stop it when you finish.");
  }
  async function perform(action: () => Promise<void>) {
    if (actionLock.current) return;
    actionLock.current = true;
    setBusy(true); setActionError(null); setNotice(null);
    try { await action(); } catch (error) { setActionError(plannerError(error)); } finally { actionLock.current = false; setBusy(false); }
  }
  function move(direction: number) {
    if (view === "week") setAnchor(dateAdd(anchor, direction * 7));
    else { const date = new Date(`${anchor.slice(0, 7)}-01T12:00:00Z`); date.setUTCMonth(date.getUTCMonth() + direction); setAnchor(date.toISOString().slice(0, 10)); }
  }

  const presentation = {
    header: <><PageHeader className="planner-heading" title="Study Plan" titleId="planner-title" description="Give your review a plan. Keep actual study time separate."
      meta={context && <><InterfaceIcon name="calendar" /><span>{dateLabel(today, { weekday: "long", month: "long", day: "numeric" })}</span><span className="context-chip">{timezone}</span></>}
      actions={<button type="button" className="primary-button" disabled={!context || !subjectsKnown} onClick={() => setDialog(tab === "tasks" ? { kind: "task" } : { kind: "event", date: tab === "calendar" && window.matchMedia("(max-width: 959px)").matches ? selectedDay : today })}><InterfaceIcon name="plus" />{tab === "tasks" ? "New task" : "New event"}</button>} />
<nav className="planner-tabs" aria-label="Study planner views">{(["calendar", "today", "tasks"] as Tab[]).map((value) => <button type="button" key={value} aria-current={tab === value ? "page" : undefined} onClick={() => setTab(value)}>{value[0].toUpperCase() + value.slice(1)}</button>)}</nav></>,
    feedback: <>{loading && (context ? <LoadingNotice>Refreshing planner…</LoadingNotice> : <ContentSkeleton label="Loading planner…" layout="calendar" />)}
{error && <div className="curriculum-state"><p role="alert" className="auth-error">{error}</p><button type="button" className="secondary-button" onClick={refresh}>Refresh planner</button></div>}
{context && <>{actionError && <div className="planner-action-error"><p role="alert" className="auth-error">{actionError}</p><button type="button" className="secondary-button" disabled={busy} onClick={refresh}>Refresh planner</button></div>}
{notice && <p role="status" className="planner-notice">{notice}</p>}</>}</>,
    overview: <>{context && <div className="planner-overview">
        <dl className="summary-strip planner-summary" aria-label="Planning overview" aria-busy={loading || (tab !== "tasks" && eventsLoading)}>
          <SummaryMetric label={tab === "tasks" ? "Task list" : "Events in view"} value={tab === "tasks" ? tasksKnown ? tasks.length : "—" : !loadedPeriod ? "—" : events.length} detail={tab === "tasks" ? "Saved study tasks" : eventPending ? "Updating selected period; last loaded count shown" : eventError ? "Could not load this period" : tab === "today" ? "Today's calendar" : "All dates shown in this calendar"} icon="calendar" />
          <SummaryMetric label="Pending tasks" value={tasksKnown ? tasks.filter((task) => task.status === "pending").length : "—"} detail={tasksKnown ? "Ready to schedule" : "Tasks unavailable"} icon="quizzes" tone="highlight" />
        </dl>
      <section className="planner-session" aria-label="Actual study time" data-active={!!context.active_session}><div className="planner-session-copy"><div className="planner-session-state"><InterfaceIcon name="focus" /><span>{context.active_session ? "Session active" : "Focus session"}</span></div><h2>{context.active_session ? "Study session in progress" : "Record actual study time"}</h2><p>{context.active_session ? `Started ${dateLabel(zonedParts(context.active_session.started_at, timezone).date)} at ${zonedParts(context.active_session.started_at, timezone).time} (${timezone}).` : "Start a session here or from a calendar event. Planned time stays separate."}</p></div><button type="button" className="secondary-button" disabled={busy || loading} onClick={() => void perform(async () => {
        if (context.active_session) { const finished = await stopSession(context.active_session.id); setNotice(`Session stopped. ${Math.floor((finished.duration_seconds ?? 0) / 60)} minutes recorded.`); setContext((current) => current ? { ...current, active_session: null } : current); }
        else await beginSession();
      })} aria-busy={busy}><PendingLabel pending={busy} idle={context.active_session ? "Stop session" : "Start session"} busy={"Saving…"} /></button></section>
      </div>}</>,
    content: <>{context && <>{tab === "tasks" ? <section aria-labelledby="task-list-title"><div className="section-heading"><h2 id="task-list-title">Study tasks</h2><span>{tasksKnown ? `${tasks.length} ${tasks.length === 1 ? "task" : "tasks"}` : loading ? "Loading tasks…" : "Tasks unavailable"}</span></div>
        {!tasksKnown ? loading ? <ContentSkeleton label="Loading tasks…" /> : <p role="alert" className="auth-error">Tasks are unavailable. Refresh planner to retry.</p> : !tasks.length ? <div className="curriculum-state"><h3>No study tasks yet</h3><p>Add work to organize before choosing a study time.</p></div> : <ul className="planner-task-list">{tasks.map((task) => {
          const subject = subjectFor(task.subject_id), due = task.due_at ? zonedParts(task.due_at, timezone) : null;
          return <li className="planner-task" key={task.id}><span className="subject-marker" data-color={subject?.color_key ?? undefined} aria-hidden="true" /><div className="planner-task-copy"><h3>{task.title}</h3><p>{subject?.code ?? "General"} · {task.task_type} · {task.status}{task.estimated_minutes ? ` · ${task.estimated_minutes} min planned` : ""}</p>{due && <p>Due {dateLabel(due.date)} at {due.time}{task.status !== "completed" && task.status !== "cancelled" && new Date(task.due_at!) < new Date() ? " · overdue" : ""}</p>}</div><div className="planner-task-actions">
            <button type="button" className="secondary-button" disabled={busy || loading} onClick={() => setDialog({ kind: "task", task })}>Edit</button>
            {task.status === "pending" && <button type="button" className="secondary-button" disabled={busy || loading} onClick={() => setDialog({ kind: "event", task, date: today })}>Schedule</button>}
            {task.scheduled_event_id && <button type="button" className="secondary-button" disabled={busy || loading} onClick={() => void perform(async () => { const event = await getEvent(task.scheduled_event_id!); setDialog({ kind: "event", event, date: zonedParts(event.start_at, event.timezone).date }); })}>Linked event</button>}
            {task.status !== "completed" && task.status !== "cancelled" && <button type="button" className="secondary-button" disabled={busy || loading} onClick={() => void perform(async () => { await updateTask(task.id, { status: "completed" }); saved(); })}>Complete</button>}
          </div></li>;
        })}</ul>}
      </section> : <>
        <div className="planner-calendar-toolbar"><div className="planner-period-controls">{tab === "calendar" && <><button type="button" className="secondary-button" aria-label={`Previous ${view}`} onClick={() => move(-1)}><InterfaceIcon name="previous" /></button><button type="button" className="secondary-button" onClick={() => setAnchor(today)}>Today</button><button type="button" className="secondary-button" aria-label={`Next ${view}`} onClick={() => move(1)}><InterfaceIcon name="next" /></button></>}<h2>{tab === "today" ? dateLabel(today, { weekday: "long", month: "long", day: "numeric" }) : view === "month" ? dateLabel(anchor, { month: "long", year: "numeric" }) : `${dateLabel(days[0])} – ${dateLabel(days[6], { month: "short", day: "numeric", year: "numeric" })}`}</h2></div>{tab === "calendar" && <div className="planner-view-controls" aria-label="Calendar layout">{(["month", "week"] as const).map((value) => <button type="button" key={value} className="secondary-button" aria-pressed={view === value} onClick={() => setView(value)}>{value === "month" ? "Month" : "Week"}</button>)}</div>}</div>
        <p className="planner-timezone">Times shown in {timezone}. Select a date or time to add an event.</p>
        {eventError && <div className="resource-error"><p className="auth-error" role="alert">{eventError}{loadedPeriod && " Showing the last loaded calendar."}</p><button type="button" className="secondary-button" onClick={refresh}>Try again</button></div>}{loadedPeriod && eventPending && <LoadingNotice>Updating study events… Keeping the last loaded calendar visible.</LoadingNotice>}{loadedPeriod && !samePeriod && <p className="resource-note">Last loaded dates: {dateLabel(shownTab === "today" ? shownToday : shownDays[0])}{shownTab !== "today" && ` – ${dateLabel(shownDays[shownDays.length - 1])}`}. The selected period will appear after it loads.</p>}{!loadedPeriod ? !eventError && <ContentSkeleton label="Loading study events…" layout="calendar" /> : shownTab === "today" ? <div className="planner-agenda">{eventsOn(shownToday).length ? eventsOn(shownToday).map((event) => <div className="planner-today-row" key={`${event.id}/${event.occurrence_date ?? "one"}`}>{eventButton(event)}{event.status === "scheduled" && <button type="button" className="secondary-button" aria-label={`Complete ${event.title}`} disabled={busy || loading} onClick={() => void perform(async () => { await updateEvent(event, { status: "completed" }); saved(); })}>Complete</button>}</div>) : <div className="curriculum-state"><h3>No study events in this loaded day</h3><p>Add a study event or schedule a task when you are ready.</p><button className="secondary-button" onClick={() => setDialog({ kind: "event", date: today })}>Add today&apos;s event</button></div>}</div> : <>
          {events.length === 0 && !eventPending && <p className="planner-note planner-period-empty">No events in this period. Select a date or time to plan your review.</p>}
          <ResponsiveView layout="calendar" desktop={() => <PlanDesktopCalendar view={shownView} days={shownDays} anchor={shownAnchor} today={today} pending={eventPending} timezone={timezone} eventsOn={eventsOn} eventButton={eventButton} onAdd={(date, time) => setDialog({ kind: "event", date, time })} />} mobile={() => <PlanMobileCalendar anchor={shownAnchor} view={shownView} days={compactDays} today={today} selectedDate={selectedDay} timezone={timezone} subjects={subjects} pending={eventPending} disabled={busy || !subjectsKnown} eventsForDate={eventsOn} onSelect={setSelectedDate} onAdd={date => setDialog({ kind: "event", date })} onEdit={event => setDialog({ kind: "event", event, date: zonedParts(event.start_at, timezone).date })} />} />
        </>}
      </>}</>}</>,
  };
  return <><ResponsiveView layout="calendar" desktop={() => <PlanDesktopView {...presentation} />} mobile={() => <PlanMobileView {...presentation} />} />
{dialog?.kind === "event" && <EventDialog {...dialog} subjects={subjects} timezone={timezone} saved={saved} close={() => setDialog(null)} beginSession={beginSession} />}
{dialog?.kind === "task" && <TaskDialog {...dialog} subjects={subjects} timezone={timezone} saved={saved} close={() => setDialog(null)} />}
</>;
}
