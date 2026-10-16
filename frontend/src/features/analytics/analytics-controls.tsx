import Link from "next/link";
import { PageHeader } from "@/components/page-header";
import { rangeError } from "./presentation";
import type { AnalyticsViewProps } from "./use-analytics-data";
export function AnalyticsControls({ model, compact = false }: { model: AnalyticsViewProps; compact?: boolean }) {
  const { range, custom, setCustom, start, setStart, end, setEnd, dateError, setDateError, summary, history, data, busy, today, chooseRange } = model;
  return <>
    <PageHeader title="Analytics" description="Compare completed study time with your plan." actions={<><Link href="/focus" className="secondary-button">Open Focus</Link><button type="button" className="ghost-button" disabled={busy} onClick={() => { summary.retry(); history.retry(); }}>Refresh</button></>} />
    <div className="study-periods ui-toolbar" aria-label="Analytics period">
      {([7, 30, 90] as const).map((period) => <button type="button" key={period} className="secondary-button" aria-pressed={!custom && "period" in range && range.period === period} onClick={() => { setCustom(false); chooseRange({ period }); }}>{compact ? `${period} days` : `Last ${period} days`}</button>)}
      <button type="button" className="secondary-button" aria-pressed={custom} onClick={() => { setCustom(true); setStart(data?.start_date ?? ""); setEnd(data?.end_date ?? ""); }}>Custom range</button>
    </div>
    {custom && <form className="resource-filters study-range-form" onSubmit={(event) => { event.preventDefault(); const error = rangeError(start, end, today); setDateError(error); if (!error) chooseRange({ start_date: start, end_date: end }); }}><label>Start date<input type="date" required value={start} max={end || today} onChange={(event) => setStart(event.target.value)} /></label><label>End date<input type="date" required value={end} min={start} max={today} onChange={(event) => setEnd(event.target.value)} /></label><button className="secondary-button" disabled={!today || busy}>Apply range</button><span className="resource-note">Up to 90 days, including both dates.</span></form>}
    {dateError && <p className="auth-error" role="alert">{dateError}</p>}
  </>;
}
