import { useLayoutEffect, useRef, useState, type ReactNode } from "react";
import type { Subject } from "@/services/subjects";
import type { StudyEvent } from "@/services/study-plan";
import { InterfaceIcon } from "@/components/interface-icon";
import { StatusBadge } from "@/components/study-ui";
import { dateLabel, zonedParts } from "./dates";

type Props = {
  anchor: string; view: "month" | "week"; days: string[]; today: string; selectedDate: string;
  timezone: string; subjects: Subject[]; pending: boolean; disabled?: boolean;
  eventsForDate: (date: string) => StudyEvent[];
  onSelect: (date: string) => void; onAdd: (date: string) => void; onEdit: (event: StudyEvent) => void;
};

// Only removed rows linger briefly; date changes remount this keyed agenda.
function AgendaEvents({ events, pending, children }: { events: StudyEvent[]; pending: boolean; children: (event: StudyEvent) => ReactNode }) {
  const previous = useRef(events);
  const [leaving, setLeaving] = useState<StudyEvent[]>([]);
  const identity = events.map(event => `${event.id}/${event.occurrence_date ?? "one"}`).join("|");
  useLayoutEffect(() => {
    const removed = previous.current.filter(event => !events.some(current => current.id === event.id && current.occurrence_date === event.occurrence_date));
    previous.current = events;
    if (!removed.length || window.matchMedia("(prefers-reduced-motion: reduce)").matches) { setLeaving([]); return; }
    setLeaving(removed);
    const timer = window.setTimeout(() => setLeaving([]), 160);
    return () => window.clearTimeout(timer);
  // Contents update immediately; this effect tracks row presence only.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [identity]);
  return events.length || leaving.length ? <ul className="compact-agenda-list">
    {events.map(event => <li key={`${event.id}/${event.occurrence_date ?? "one"}`}>{children(event)}</li>)}
    {leaving.map(event => <li className="compact-row-leaving" inert aria-hidden="true" key={`leaving/${event.id}/${event.occurrence_date ?? "one"}`}>{children(event)}</li>)}
  </ul> : <p className="compact-agenda-empty" role="status">{pending ? "Checking the selected day…" : "No study blocks planned."}</p>;
}

export function CompactCalendar({ anchor, view, days, today, selectedDate, timezone, subjects, pending, disabled, eventsForDate, onSelect, onAdd, onEdit }: Props) {
  const labels = view === "month" ? ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"] : ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const events = [...eventsForDate(selectedDate)].sort((a, b) => Date.parse(a.start_at) - Date.parse(b.start_at) || a.id.localeCompare(b.id));
  const subjectFor = (id: string | null) => subjects.find(subject => subject.id === id);
  return <div className="planner-compact" aria-busy={pending}>
    <div className="compact-date-picker" role="group" aria-label={`Select a study date in ${dateLabel(anchor, { month: "long", year: "numeric" })}`}>
      {view === "month" && <div className="compact-weekdays" aria-hidden="true">{labels.map(label => <span key={label}>{label}</span>)}</div>}
      <div className={view === "month" ? "compact-month-grid" : "compact-week-strip"} key={`${view}:${anchor.slice(0, 7)}:${days[0]}`}>
        {days.map((date, index) => {
          const dayEvents = eventsForDate(date);
          return <button type="button" className="compact-day" data-date={date} key={date} data-outside={view === "month" && date.slice(0, 7) !== anchor.slice(0, 7)} data-today={date === today} aria-current={date === today ? "date" : undefined} aria-pressed={date === selectedDate} tabIndex={date === selectedDate ? 0 : -1} aria-controls="selected-day-agenda" aria-label={`${dateLabel(date, { weekday: "long", month: "long", day: "numeric", year: "numeric" })}, ${dayEvents.length} study ${dayEvents.length === 1 ? "block" : "blocks"}`} onClick={() => onSelect(date)} onKeyDown={event => {
            const step = { ArrowLeft: -1, ArrowRight: 1, ArrowUp: -7, ArrowDown: 7, Home: -(index % 7), End: 6 - index % 7 }[event.key];
            if (step === undefined || !days[index + step]) return;
            event.preventDefault(); const next = days[index + step]; onSelect(next);
            event.currentTarget.parentElement?.querySelector<HTMLButtonElement>(`[data-date="${next}"]`)?.focus();
          }}>
            {view === "week" && <span className="compact-weekday-name">{dateLabel(date, { weekday: "short" })}</span>}<span className="compact-day-number">{Number(date.slice(-2))}</span>
            <span className="compact-day-markers" aria-hidden="true">{dayEvents.slice(0, 3).map(event => <i className="subject-marker" data-color={subjectFor(event.subject_id)?.color_key ?? undefined} key={`${event.id}/${event.occurrence_date ?? "one"}`} />)}{dayEvents.length > 3 && <small>+{dayEvents.length - 3}</small>}</span>
          </button>;
        })}
      </div>
    </div>
    <section className="compact-day-agenda" id="selected-day-agenda" aria-labelledby="selected-day-title">
      <header><h3 id="selected-day-title">{dateLabel(selectedDate, { weekday: "long", month: "long", day: "numeric" })}</h3><span>{pending ? "Updating…" : `${events.length} ${events.length === 1 ? "study block" : "study blocks"}`}</span></header>
      <div className="compact-agenda-content" data-view={view} key={selectedDate}>
        <AgendaEvents events={events} pending={pending}>{event => {
          const subject = subjectFor(event.subject_id), start = zonedParts(event.start_at, timezone);
          return <button type="button" className="compact-agenda-event" disabled={disabled} aria-label={`Edit ${event.title} at ${start.time}`} data-subject={subject?.code} onClick={() => onEdit(event)}>
            <span className="compact-event-times"><time dateTime={event.start_at}>{start.date === selectedDate ? start.time : dateLabel(start.date)}</time>{view === "week" && <><span aria-hidden="true">—</span><time dateTime={event.end_at}>{zonedParts(event.end_at, timezone).time}</time></>}</span><span className="subject-marker" data-color={subject?.color_key ?? undefined} aria-hidden="true" />
            <span className="compact-event-copy"><span>{subject?.code ?? "General study"}{event.is_recurring && " · Repeats"}</span><strong>{event.title}</strong><StatusBadge tone={event.status === "completed" ? "success" : "neutral"}>{event.status}</StatusBadge></span><InterfaceIcon name="next" />
          </button>;
        }}</AgendaEvents>
        <button type="button" className="compact-agenda-add secondary-button" disabled={disabled} onClick={() => onAdd(selectedDate)}><InterfaceIcon name="plus" />Add study event</button>
      </div>
    </section>
  </div>;
}
