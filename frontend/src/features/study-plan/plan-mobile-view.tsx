import type { PlanViewProps } from "./plan-view-types";
import type { ComponentProps } from "react";
import { CompactCalendar } from "./compact-calendar";
/** Month picker / Week strip + selected-date timeline; no hidden desktop calendar. */
export function PlanMobileCalendar(props: ComponentProps<typeof CompactCalendar>) {
  return <CompactCalendar {...props} />;
}

export function PlanMobileView({header, feedback, overview, content}: PlanViewProps) {
  return <section className="study-planner plan-mobile" aria-labelledby="planner-title">{header}{feedback}{content}{overview}</section>;
}
