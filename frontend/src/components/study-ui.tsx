import type { ReactNode } from "react";

/** Presentation only: callers retain data, actions and status semantics. */
export function SectionHeader({ title, titleId, detail, actions }: {
  title: string; titleId?: string; detail?: ReactNode; actions?: ReactNode;
}) {
  return <header className="ui-section-heading section-header">
    <div><h2 id={titleId}>{title}</h2>{detail && <p className="section-header-detail">{detail}</p>}</div>
    {actions && <div className="ui-toolbar">{actions}</div>}
  </header>;
}

export function StatusBadge({ children, tone = "neutral" }: {
  children: ReactNode; tone?: "neutral" | "info" | "success" | "warning" | "danger";
}) {
  return <span className="status-badge" data-tone={tone}>{children}</span>;
}

/** Shows provided counts without estimating unknown durations or a composite score. */
export function ProgressMeter({ value, total, label, tone = "accent" }: {
  value: number; total: number; label: string; tone?: "accent" | "info";
}) {
  return <div className="progress-meter" data-tone={tone}>
    <div className="progress-meter-caption"><span>{label}</span><span>{value} / {total}</span></div>
    {total > 0 && <progress value={value} max={total} aria-label={label} />}
  </div>;
}

export function LoadingNotice({ children = "Loading study data…" }: { children?: ReactNode }) {
  return <div className="loading-notice" role="status"><span className="loading-notice-mark" aria-hidden="true" /><span>{children}</span></div>;
}
