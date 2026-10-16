import Link from "next/link";
import type { AssessmentListViewProps } from "./assessment-desktop-view";
import { StatusBadge } from "@/components/study-ui";
import { assessmentTimestamp } from "./form-state";

export function AssessmentMobileView({ groups, timezone }: AssessmentListViewProps) {
  return <div className="mobile-assessment-groups">{groups.map(group => <section key={group.title}><header className="ui-section-heading"><h2>{group.title}</h2><span>{group.items.length}</span></header><ul>{group.items.map(assessment => <li key={assessment.id}>
    <h3><Link href={`/assessments/${assessment.id}`}>{assessment.title}</Link></h3><div className="mobile-assessment-meta"><span>{assessment.scheduled_at ? timezone ? assessmentTimestamp(assessment.scheduled_at,timezone) : "Date awaiting timezone" : "Date not set"}</span><StatusBadge tone={assessment.status === "completed" ? "success" : assessment.status === "planned" ? "info" : "neutral"}>{assessment.status}</StatusBadge></div>
    <p>{assessment.topic_count} topics · {assessment.coverage_subjects.length} subjects</p><p className="mobile-coverage-codes">{assessment.coverage_subjects.map(subject => subject.code).join(" · ") || "Coverage not selected"}</p>
    <Link className="secondary-button" href={`/assessments/${assessment.id}`}>View assessment</Link>
  </li>)}</ul></section>)}</div>;
}
