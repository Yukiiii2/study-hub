import { dateLabel, weekday } from "@/features/study-plan/dates";
import type { DailyActivity } from "@/services/analytics";
import { studyDuration } from "./presentation";

export function DailyChart({ daily }: { daily: DailyActivity[] }) {
  const maximum = Math.max(1, ...daily.map((day) => day.duration_seconds));
  const x = (index: number) => 20 + index / Math.max(1, daily.length - 1) * 760;
  const y = (seconds: number) => 160 - seconds / maximum * 140;
  return <>
    <div className="study-chart-scale"><span>{studyDuration(maximum === 1 && !daily.some((day) => day.duration_seconds) ? 0 : maximum)}</span><span>Completed study time</span></div>
    <svg className="study-daily-chart" viewBox="0 0 800 180" role="img" aria-label={`Daily completed study time, ${daily.length} days. Exact values are available in Daily values.`}>
      <line x1="20" y1="160" x2="780" y2="160" className="study-chart-baseline" />
      <polyline points={daily.map((day, index) => `${x(index)},${y(day.duration_seconds)}`).join(" ")} fill="none" className="study-chart-line" />
      {daily.map((day, index) => <circle key={day.date} cx={x(index)} cy={y(day.duration_seconds)} r={daily.length <= 30 ? 3 : 2} className="study-chart-point"><title>{`${day.date}: ${studyDuration(day.duration_seconds)}, ${day.session_count} sessions`}</title></circle>)}
    </svg>
    <div className="study-chart-scale"><span>0:00:00 · {daily[0] && dateLabel(daily[0].date)}</span><span>{daily.length > 0 && dateLabel(daily[daily.length - 1].date)}</span></div>
    <details className="study-daily-values"><summary>Daily values</summary><ul className="study-daily-values-list">{daily.map((day) => <li key={day.date}><time dateTime={day.date}>{dateLabel(day.date, { weekday: "short", month: "short", day: "numeric" })}</time><span>{studyDuration(day.duration_seconds)} · {day.session_count} sessions</span></li>)}</ul></details>
  </>;
}

export function CalendarHeatmap({ daily }: { daily: DailyActivity[] }) {
  const maximum = Math.max(0, ...daily.map((day) => day.duration_seconds));
  const offset = daily.length ? (weekday(daily[0].date) + 6) % 7 : 0;
  return <>
    <p className="resource-note">Each column is a week, Monday to Sunday. Focus a date for its recorded time.</p>
    <ul className="study-heatmap" aria-label="Daily completed study activity, Monday to Sunday in each column">
      {Array.from({ length: offset }, (_, index) => <li key={`blank-${index}`} className="study-heatmap-spacer" aria-hidden="true" />)}
      {daily.map((day) => {
        const level = day.duration_seconds === 0 ? 0 : Math.min(4, Math.max(1, Math.ceil(day.duration_seconds / maximum * 4)));
        const label = `${dateLabel(day.date, { weekday: "long", month: "long", day: "numeric", year: "numeric" })}: ${studyDuration(day.duration_seconds)}, ${day.session_count} completed sessions`;
        return <li key={day.date} className="study-heatmap-day" data-level={level} tabIndex={0} aria-label={label} title={label}><span className="sr-only">{label}</span><span aria-hidden="true">{Number(day.date.slice(8))}</span></li>;
      })}
    </ul>
    <p className="resource-note">Empty cells mean zero recorded time. Darker to lighter cells show less to more time within this range.</p>
  </>;
}

export function TimeBar({ label, seconds, maximum, planned = false }: { label: string; seconds: number; maximum: number; planned?: boolean }) {
  return <div className="study-time-bar"><span>{label}</span><div className="study-bar-track" aria-hidden="true"><div className="study-bar-fill" data-planned={planned} style={{ width: `${maximum ? seconds / maximum * 100 : 0}%` }} /></div><strong>{studyDuration(seconds)}</strong></div>;
}
