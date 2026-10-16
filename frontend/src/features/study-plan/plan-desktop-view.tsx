import type { PlanViewProps } from "./plan-view-types";
import type { ReactNode } from "react";
import type { StudyEvent } from "@/services/study-plan";
import { InterfaceIcon } from "@/components/interface-icon";
import { dateLabel, zonedParts } from "./dates";
const weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const hours = Array.from({ length: 12 }, (_, index) => index * 2);
export function PlanDesktopCalendar({ view, days, anchor, today, pending, eventsOn, eventButton, onAdd, timezone }: {
  view: "month" | "week"; days: string[]; anchor: string; today: string; pending: boolean; timezone: string;
  eventsOn: (date: string) => StudyEvent[]; eventButton: (event: StudyEvent, compact?: boolean) => ReactNode;
  onAdd: (date: string, time?: string) => void;
}) {
  return <div className={`planner-calendar planner-${view}`} role="region" aria-busy={pending} aria-label={`${view} calendar`}>
            {view === "month" ? <><div className="planner-week-header">{weekdays.map((day) => <span key={day}>{day}</span>)}</div><div className="planner-month-grid">{days.map((date) => <section className="planner-month-day" data-outside={date.slice(0, 7) !== anchor.slice(0, 7)} data-today={date === today} key={date} aria-label={dateLabel(date, { weekday: "long", month: "long", day: "numeric" })}><button type="button" className="planner-date-button" aria-current={date === today ? "date" : undefined} aria-label={`Add event on ${dateLabel(date)}`} onClick={() => onAdd(date)}>{Number(date.slice(-2))}</button>{eventsOn(date).map((event) => eventButton(event, true))}</section>)}</div></> : <div className="planner-week-grid"><div className="planner-week-times" aria-hidden="true"><div className="planner-week-day-header" style={{ gridColumn: 1, gridRow: 1 }}>Time</div>{hours.map((hour, hourIndex) => <div className="planner-hour" style={{ gridColumn: 1, gridRow: hourIndex + 2 }} key={hour}>{`${String(hour).padStart(2, "0")}:00`}</div>)}</div>{days.map((date, dayIndex) => <section className="planner-week-column" key={date} data-today={date === today} aria-label={dateLabel(date, { weekday: "long", month: "long", day: "numeric" })}><button className="planner-week-day-header" aria-current={date === today ? "date" : undefined} style={{ gridColumn: dayIndex + 2, gridRow: 1 }} onClick={() => onAdd(date)}>{dateLabel(date, { weekday: "short", day: "numeric" })}</button>{hours.map((hour, hourIndex) => <div className="planner-time-cell" style={{ gridColumn: dayIndex + 2, gridRow: hourIndex + 2 }} key={hour}><button className="planner-time-add" aria-label={`Add event on ${dateLabel(date)} at ${String(hour).padStart(2, "0")}:00`} onClick={() => onAdd(date, `${String(hour).padStart(2, "0")}:00`)}><InterfaceIcon name="plus" /></button>{eventsOn(date).filter((event) => { const start = zonedParts(event.start_at, timezone); const startHour = start.date < date ? 0 : Number(start.time.slice(0, 2)); return startHour >= hour && startHour < hour + 2; }).map((event) => eventButton(event, true))}</div>)}</section>)}</div>}
          </div>;
}

export function PlanDesktopView({header, feedback, overview, content}: PlanViewProps) {
  return <section className="study-planner plan-desktop" aria-labelledby="planner-title">{header}{feedback}{overview}{content}</section>;
}
