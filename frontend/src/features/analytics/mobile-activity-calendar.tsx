import { useState } from "react";
import type { DailyActivity } from "@/services/analytics";
import { compactMonthDays, dateLabel } from "@/features/study-plan/dates";
import { studyDuration } from "./presentation";

/** A readable month at a time, rather than a horizontally squeezed 90-day heatmap. */
export function MobileActivityCalendar({ daily }: { daily: DailyActivity[] }) {
  const months = [...new Set(daily.map(day => day.date.slice(0,7)))];
  const [chosenMonth, chooseMonth] = useState("");
  const [selected, select] = useState<string | null>(null);
  const month = months.includes(chosenMonth) ? chosenMonth : months.at(-1);
  const current = daily.find(day => day.date === selected);
  const maximum = Math.max(0,...daily.map(day => day.duration_seconds));
  if (!month) return <p className="resource-note">No study dates in this range.</p>;
  return <div className="mobile-activity-calendar"><label>Month<select value={month} onChange={event => { chooseMonth(event.target.value); select(null); }}>{months.map(value => <option key={value} value={value}>{dateLabel(`${value}-01`,{month:"long",year:"numeric"})}</option>)}</select></label>
    <div className="compact-weekdays" aria-hidden="true">{["Sun","Mon","Tue","Wed","Thu","Fri","Sat"].map(day => <span key={day}>{day}</span>)}</div>
    <div className="mobile-activity-days">{compactMonthDays(`${month}-01`).map(date => {
      if (date.slice(0,7) !== month) return <span key={date} aria-hidden="true" />;
      const day = daily.find(item => item.date === date), level = day && day.duration_seconds > 0 ? Math.min(4,Math.max(1,Math.ceil(day.duration_seconds / maximum * 4))) : 0;
      return <button type="button" key={date} disabled={!day} data-level={level} aria-pressed={selected === date} aria-label={`${dateLabel(date)}: ${day ? `${studyDuration(day.duration_seconds)}, ${day.session_count} sessions` : "Outside selected report range"}`} onClick={() => select(date)}>{Number(date.slice(-2))}</button>;
    })}</div><p className="resource-note" role="status">{current ? `${dateLabel(current.date)}: ${studyDuration(current.duration_seconds)}, ${current.session_count} completed sessions.` : "Select a date for its recorded time. Shading shows relative study time; disabled dates are outside this report."}</p>
  </div>;
}
