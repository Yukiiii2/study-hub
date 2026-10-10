"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";
import { getSubjectTopics, type Subject, type Topic } from "@/services/subjects";
import { createEvent, createTask, deleteEvent, deleteTask, eventTypes, getEvent, plannerError, scheduleTask, updateEvent, updateTask, type EventCreate, type EventStatus, type EventType, type StudyEvent, type StudyTask, type TaskInput } from "@/services/study-plan";
import { localToInstant, weekday, zonedParts } from "./dates";

function Dialog({ title, busy, close, children }: { title: string; busy: boolean; close: () => void; children: ReactNode }) {
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => { const element = dialog.current; element?.showModal(); return () => element?.close(); }, []);
  return <dialog ref={dialog} className="planner-dialog" aria-labelledby="planner-dialog-title" onCancel={(event) => { event.preventDefault(); if (!busy) close(); }}>
    <div className="planner-dialog-heading"><h2 id="planner-dialog-title">{title}</h2><button type="button" className="secondary-button" disabled={busy} onClick={close} aria-label="Close dialog">Close</button></div>
    {children}
  </dialog>;
}

function useTopics(subjectId: string) {
  const [state, setState] = useState<{ subject: string; topics: Topic[]; error: string | null } | null>(null);
  const [retry, setRetry] = useState(0);
  useEffect(() => {
    if (!subjectId) return;
    const controller = new AbortController();
    setState(null);
    void getSubjectTopics(subjectId, controller.signal).then((topics) => {
      if (!controller.signal.aborted) setState({ subject: subjectId, topics, error: null });
    }).catch(() => {
      if (!controller.signal.aborted) setState({ subject: subjectId, topics: [], error: "Could not load topics. Try again before saving." });
    });
    return () => controller.abort();
  }, [subjectId, retry]);
  const current = state?.subject === subjectId ? state : null;
  return { topics: current?.topics ?? [], error: current?.error ?? null, loading: !!subjectId && !current, retry: () => setRetry((value) => value + 1) };
}

function Associations({ subjects, subject, topic, onSubject, onTopic, topics, loading, error, retry, locked = false }: { subjects: Subject[]; subject: string; topic: string; onSubject: (value: string) => void; onTopic: (value: string) => void; topics: Topic[]; loading: boolean; error: string | null; retry: () => void; locked?: boolean }) {
  return <>
    <label>Subject<select value={subject} disabled={locked} onChange={(event) => onSubject(event.target.value)}><option value="">No subject</option>{subjects.map((value) => <option key={value.id} value={value.id}>{value.code} — {value.name}</option>)}</select></label>
    <label>Topic<select value={topic} disabled={!subject || loading || !!error || locked} onChange={(event) => onTopic(event.target.value)}><option value="">{loading ? "Loading topics…" : "No topic"}</option>{topics.map((value) => <option value={value.id} key={value.id}>{value.code ? `${value.code} — ` : ""}{value.title}</option>)}</select></label>
    {error && <div className="planner-field-error"><p className="auth-error" role="alert">{error}</p><button className="secondary-button" type="button" onClick={retry}>Retry topics</button></div>}
    {topic && !loading && !error && !topics.some((value) => value.id === topic) && <p className="auth-error" role="alert">The selected topic is unavailable. Choose another topic or no topic.</p>}
  </>;
}

const weekdays = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"];
const dayNames = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
function eventFields(event: StudyEvent | undefined, date: string, time: string, timezone: string, task?: StudyTask) {
  const start = event ? zonedParts(event.start_at, event.timezone) : { date, time };
  const end = event ? zonedParts(event.end_at, event.timezone) : zonedParts(new Date(Date.parse(`${date}T${time}:00Z`) + (task?.estimated_minutes ?? 60) * 60000), "UTC");
  const rule = event?.recurrence_rule;
  return { title: event?.title ?? task?.title ?? "", subject: event?.subject_id ?? task?.subject_id ?? "", topic: event?.topic_id ?? task?.topic_id ?? "", type: event?.event_type ?? task?.task_type ?? "general", date: start.date, start: start.time, endDate: end.date, end: end.time, timezone: event?.timezone ?? timezone, status: event?.status ?? "scheduled", notes: event?.notes ?? "", recurring: !!rule, days: rule?.match(/BYDAY=([^;]+)/)?.[1].split(",") ?? [weekdays[(weekday(start.date) + 6) % 7]], until: rule?.match(/UNTIL=(\d{8})/)?.[1].replace(/^(\d{4})(\d{2})(\d{2})$/, "$1-$2-$3") ?? "" };
}

export function EventDialog({ event, task, date, time = "09:00", timezone, subjects, close, saved, beginSession }: { event?: StudyEvent; task?: StudyTask; date: string; time?: string; timezone: string; subjects: Subject[]; close: () => void; saved: () => void; beginSession: (event: StudyEvent) => Promise<void> }) {
  const [fields, setFields] = useState(() => eventFields(event, date, time, timezone, task));
  const [scope, setScope] = useState<"occurrence" | "series">(event?.recurrence_rule && !event.occurrence_date ? "series" : "occurrence");
  const [busy, setBusy] = useState(false);
  const [switching, setSwitching] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fetchController = useRef<AbortController | null>(null);
  const topicState = useTopics(fields.subject);
  useEffect(() => () => fetchController.current?.abort(), []);
  const change = <K extends keyof typeof fields>(key: K, value: typeof fields[K]) => setFields((current) => ({ ...current, [key]: value }));
  const recurringOccurrence = !!event?.occurrence_date;
  const canRecur = !recurringOccurrence || scope === "series";

  async function changeScope(value: "occurrence" | "series") {
    fetchController.current?.abort(); setError(null); setConfirmDelete(false); setScope(value);
    if (value === "occurrence") { setSwitching(false); setFields(eventFields(event, date, time, timezone)); return; }
    const controller = new AbortController(); fetchController.current = controller; setSwitching(true);
    try {
      const series = await getEvent(event!.id, controller.signal);
      if (!controller.signal.aborted) setFields(eventFields(series, date, time, timezone));
    } catch (error) { if (!controller.signal.aborted) { setError(plannerError(error)); setScope("occurrence"); setFields(eventFields(event, date, time, timezone)); } }
    finally { if (!controller.signal.aborted) setSwitching(false); }
  }

  async function save() {
    setBusy(true); setError(null);
    try {
      if (!fields.title.trim()) throw new Error("Enter an event title.");
      if (topicState.loading || topicState.error) throw new Error("Wait for topics to load before saving.");
      if (fields.topic && !topicState.topics.some((topic) => topic.id === fields.topic && topic.subject_id === fields.subject)) throw new Error("Choose a topic that belongs to the selected subject.");
      if (fields.recurring && canRecur && (!fields.days.length || !fields.days.includes(weekdays[(weekday(fields.date) + 6) % 7]))) throw new Error("Include the starting date's weekday in the weekly plan.");
      if (fields.until && fields.until < fields.date && fields.recurring && canRecur) throw new Error("The repeat end date must be on or after the starting date.");
      const start = localToInstant(fields.date, fields.start, fields.timezone);
      const end = localToInstant(fields.endDate, fields.end, fields.timezone);
      if (end <= start) throw new Error("End time must be after start time.");
      const body: EventCreate = { title: fields.title.trim(), subject_id: fields.subject || null, topic_id: fields.topic || null, event_type: fields.type, start_at: start, end_at: end, timezone: fields.timezone, status: fields.recurring && canRecur ? "scheduled" : fields.status, recurrence_rule: fields.recurring && canRecur ? `FREQ=WEEKLY;BYDAY=${weekdays.filter((day) => fields.days.includes(day)).join(",")}${fields.until ? `;UNTIL=${fields.until.replaceAll("-", "")}` : ""}` : null, notes: fields.notes.trim() || null };
      if (event) {
        if (recurringOccurrence && scope === "occurrence") { const { timezone: _timezone, recurrence_rule: _rule, ...occurrence } = body; await updateEvent(event, occurrence); }
        else await updateEvent(event, body, scope === "series");
      } else if (task) await scheduleTask(task.id, body);
      else await createEvent(body);
      saved(); close();
    } catch (error) { setError(plannerError(error)); }
    finally { setBusy(false); }
  }

  async function remove() {
    setBusy(true); setError(null);
    try { await deleteEvent(event!, scope === "series"); saved(); close(); } catch (error) { setError(plannerError(error)); } finally { setBusy(false); }
  }

  return <Dialog title={event ? "Study event" : task ? "Schedule task" : "New study event"} busy={busy || switching} close={close}>
    <form className="study-editor" onSubmit={(event) => { event.preventDefault(); void save(); }}>
      {recurringOccurrence && <label className="planner-scope">Apply changes to<select value={scope} disabled={busy} onChange={(event) => void changeScope(event.target.value as "occurrence" | "series")}><option value="occurrence">Only this occurrence ({event.occurrence_date})</option><option value="series">Entire recurring series</option></select></label>}
      {event?.recurrence_rule && !recurringOccurrence && <p className="planner-note">Editing the entire recurring series. Open a calendar occurrence to change only that date or start a linked session.</p>}
      {switching && <p role="status">Loading the series…</p>}
      <fieldset disabled={busy || switching} className="planner-form-grid">
        <label className="planner-wide">Title<input autoFocus required maxLength={200} value={fields.title} onChange={(event) => change("title", event.target.value)} /></label>
        <Associations subjects={subjects} subject={fields.subject} topic={fields.topic} onSubject={(subject) => setFields((current) => ({ ...current, subject, topic: "" }))} onTopic={(topic) => change("topic", topic)} {...topicState} locked={!!task} />
        <label>Type<select value={fields.type} onChange={(event) => change("type", event.target.value as EventType)}>{eventTypes.map((type) => <option key={type} value={type}>{type === "general" ? "General study" : type[0].toUpperCase() + type.slice(1)}</option>)}</select></label>
        <label>Status<select disabled={fields.recurring && canRecur} value={fields.recurring && canRecur ? "scheduled" : fields.status} onChange={(event) => change("status", event.target.value as EventStatus)}>{["scheduled", "completed", "skipped", "cancelled"].map((status) => <option key={status} value={status}>{status[0].toUpperCase() + status.slice(1)}</option>)}</select></label>
        <label>Start date<input type="date" required value={fields.date} onChange={(event) => change("date", event.target.value)} /></label><label>Start time<input type="time" required value={fields.start} onChange={(event) => change("start", event.target.value)} /></label>
        <label>End date<input type="date" required value={fields.endDate} onChange={(event) => change("endDate", event.target.value)} /></label><label>End time<input type="time" required value={fields.end} onChange={(event) => change("end", event.target.value)} /></label>
        <p className="planner-wide planner-note">Times use {fields.timezone}. Editing dates or times reschedules this {scope === "series" ? "series" : "event"}.</p>
        {canRecur && <><label className="planner-check planner-wide"><input type="checkbox" checked={fields.recurring} onChange={(event) => change("recurring", event.target.checked)} />Repeat weekly</label>
          {fields.recurring && <><fieldset className="planner-wide planner-weekdays"><legend>Repeat on</legend>{weekdays.map((day, index) => <label className="planner-check" key={day}><input type="checkbox" checked={fields.days.includes(day)} onChange={(event) => change("days", event.target.checked ? [...fields.days, day] : fields.days.filter((value) => value !== day))} />{dayNames[index]}</label>)}</fieldset><label>Repeat until (optional)<input type="date" min={fields.date} value={fields.until} onChange={(event) => change("until", event.target.value)} /></label><p className="planner-note">Weekly plans keep the same local times. Status is updated per occurrence.</p></>}
        </>}
        <label className="planner-wide">Notes<textarea rows={3} maxLength={10000} value={fields.notes} onChange={(event) => change("notes", event.target.value)} /></label>
      </fieldset>
      {error && <p className="auth-error" role="alert">{error}</p>}
      {confirmDelete && <div className="planner-delete-confirm"><p>Delete {scope === "series" ? "the entire series" : recurringOccurrence ? "only this occurrence" : "this event"}? Recorded study sessions are kept.</p><button type="button" className="secondary-button planner-danger" disabled={busy} onClick={() => void remove()}>Confirm deletion</button><button type="button" className="secondary-button" disabled={busy} onClick={() => setConfirmDelete(false)}>Keep event</button></div>}
      <div className="planner-dialog-actions"><button className="primary-button" disabled={busy || switching || !!topicState.error || topicState.loading}>{busy ? "Saving…" : task ? "Schedule task" : "Save event"}</button>
        {event && <><button type="button" className="secondary-button" disabled={busy || switching || scope === "series"} onClick={async () => { setBusy(true); setError(null); try { await beginSession(event); close(); } catch (error) { setError(plannerError(error)); } finally { setBusy(false); } }}>Start study session</button><button type="button" className="secondary-button planner-danger" disabled={busy || switching} onClick={() => setConfirmDelete(true)}>Delete {scope === "series" ? "series" : "event"}</button></>}
      </div>
    </form>
  </Dialog>;
}

export function TaskDialog({ task, timezone, subjects, saved, close }: { task?: StudyTask; timezone: string; subjects: Subject[]; saved: () => void; close: () => void }) {
  const due = task?.due_at ? zonedParts(task.due_at, timezone) : null;
  const [title, setTitle] = useState(task?.title ?? "");
  const [subject, setSubject] = useState(task?.subject_id ?? "");
  const [topic, setTopic] = useState(task?.topic_id ?? "");
  const [type, setType] = useState<EventType>(task?.task_type ?? "general");
  const [estimate, setEstimate] = useState(task?.estimated_minutes?.toString() ?? "");
  const [dueAt, setDueAt] = useState(due ? `${due.date}T${due.time}` : "");
  const [status, setStatus] = useState<StudyTask["status"]>(task?.status ?? "pending");
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const topicState = useTopics(subject);
  async function save() {
    setBusy(true); setError(null);
    try {
      if (!title.trim()) throw new Error("Enter a task title.");
      if (topicState.loading || topicState.error) throw new Error("Wait for topics to load before saving.");
      if (topic && !topicState.topics.some((value) => value.id === topic && value.subject_id === subject)) throw new Error("Choose a topic that belongs to the selected subject.");
      const body: Omit<TaskInput, "status"> = { title: title.trim(), subject_id: subject || null, topic_id: topic || null, task_type: type, estimated_minutes: estimate ? Number(estimate) : null, due_at: dueAt ? localToInstant(dueAt.slice(0, 10), dueAt.slice(11), timezone) : null };
      if (task) await updateTask(task.id, { ...body, ...(status !== task.status && status !== "scheduled" ? { status } : {}) });
      else await createTask({ ...body, status: "pending" });
      saved(); close();
    } catch (error) { setError(plannerError(error)); } finally { setBusy(false); }
  }
  async function remove() {
    setBusy(true); setError(null);
    try { await deleteTask(task!.id); saved(); close(); } catch (error) { setError(plannerError(error)); } finally { setBusy(false); }
  }
  return <Dialog title={task ? "Edit study task" : "New study task"} busy={busy} close={close}><form className="study-editor" onSubmit={(event) => { event.preventDefault(); void save(); }}><fieldset className="planner-form-grid" disabled={busy}>
    <label className="planner-wide">Title<input autoFocus required maxLength={200} value={title} onChange={(event) => setTitle(event.target.value)} /></label>
    <Associations subjects={subjects} subject={subject} topic={topic} onSubject={(value) => { setSubject(value); setTopic(""); }} onTopic={setTopic} {...topicState} />
    <label>Type<select value={type} onChange={(event) => setType(event.target.value as EventType)}>{eventTypes.map((value) => <option key={value} value={value}>{value === "general" ? "General study" : value[0].toUpperCase() + value.slice(1)}</option>)}</select></label>
    <label>Estimated minutes (optional)<input type="number" min={1} step={1} value={estimate} onChange={(event) => setEstimate(event.target.value)} /></label>
    {task && <label className="planner-wide">Status<select value={status} onChange={(event) => setStatus(event.target.value as StudyTask["status"])}>{task.status === "scheduled" && <option value="scheduled" disabled>Scheduled (set by scheduling)</option>}{(["pending", "completed", "cancelled"] as const).map((value) => <option value={value} key={value}>{value[0].toUpperCase() + value.slice(1)}</option>)}</select></label>}
    {task?.scheduled_event_id && status === "pending" && status !== task.status && <p className="planner-note planner-wide">Returning this task to pending removes its calendar link. The existing calendar event remains and can be managed separately.</p>}
    <label className="planner-wide">Due date and time (optional)<input type="datetime-local" value={dueAt} onChange={(event) => setDueAt(event.target.value)} /></label><p className="planner-note planner-wide">Due time uses {timezone}. Scheduling a task creates its linked calendar event.</p>
    </fieldset>{error && <p className="auth-error" role="alert">{error}</p>}
    {confirmDelete && <div className="planner-delete-confirm"><p>Delete this task?{task?.scheduled_event_id ? " Its calendar event remains." : ""}</p><button type="button" className="secondary-button planner-danger" disabled={busy} onClick={() => void remove()}>Confirm deletion</button><button type="button" className="secondary-button" disabled={busy} onClick={() => setConfirmDelete(false)}>Keep task</button></div>}
    <div className="planner-dialog-actions"><button className="primary-button" disabled={busy || topicState.loading || !!topicState.error}>{busy ? "Saving…" : "Save task"}</button>{task && <button type="button" className="secondary-button planner-danger" disabled={busy} onClick={() => setConfirmDelete(true)}>Delete task</button>}</div></form></Dialog>;
}
