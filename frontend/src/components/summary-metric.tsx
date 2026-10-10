import type { ReactNode } from "react";
import { InterfaceIcon, type IconName } from "./interface-icon";

/** Place inside a dl.summary-strip; values are supplied by the owning feature. */
export function SummaryMetric({ label, value, detail, icon, tone }: {
  label: string;
  value: ReactNode;
  detail: ReactNode;
  icon: IconName;
  tone?: "accent" | "highlight";
}) {
  return <div className="summary-metric" data-tone={tone}>
    <dt><InterfaceIcon name={icon} /><span>{label}</span></dt>
    <dd><span className="summary-metric-value">{value}</span><span className="summary-metric-detail">{detail}</span></dd>
  </div>;
}
