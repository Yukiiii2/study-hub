"use client";

import Link from "next/link";
import { FilterPanel } from "@/components/filter-panel";
import { PageHeader } from "@/components/page-header";
import { ResponsiveView } from "@/components/responsive-view";
import { AssessmentDesktopView } from "./assessment-desktop-view";
import { AssessmentMobileView } from "./assessment-mobile-view";
import { useRouter } from "next/navigation";
import { useCallback, useState } from "react";
import { getAssessments, type AssessmentStatus } from "@/services/assessments";
import { getPlannerContext } from "@/services/study-plan";
import { LoadNotice, Pagination, useQuizLoad } from "@/features/quizzes/shared";
import { AssessmentEditor } from "./assessment-editor";
import { assessmentTimestamp } from "./form-state";
import { assessmentLoad } from "./load";

export function AssessmentListPage() {
  const router = useRouter();
  const [filters, setFilters] = useState<{ q: string; status: AssessmentStatus | "all"; offset: number }>({ q: "", status: "all", offset: 0 });
  const [search, setSearch] = useState(""), [creating, setCreating] = useState(false);
  const context = useQuizLoad(useCallback((signal) => assessmentLoad(getPlannerContext(signal)), []));
  const assessments = useQuizLoad(useCallback((signal) => assessmentLoad(getAssessments({ ...filters, limit: 20 }, signal).then((data) => ({ ...data, filters }))), [filters]));
  const timezone = context.data?.timezone;
  const visible = assessments.data?.assessments ?? [];
  const groups = [
    { title: "Upcoming", items: visible.filter(item => item.status === "planned" && item.scheduled_at && Date.parse(item.scheduled_at) >= Date.now()) },
    { title: "Scheduled date passed", items: visible.filter(item => item.status === "planned" && item.scheduled_at && Date.parse(item.scheduled_at) < Date.now()) },
    { title: "Unscheduled", items: visible.filter(item => item.status === "planned" && !item.scheduled_at) },
    { title: "History", items: visible.filter(item => item.status !== "planned") },
  ].filter(group => group.items.length);
  return <><PageHeader title="Assessments" description="Plan your coverage and keep a separate history of assessment results." actions={<button type="button" className="primary-button" disabled={!timezone || context.loading || !!context.error} onClick={() => setCreating(true)}>New assessment</button>} /><FilterPanel><form className="resource-filters ui-toolbar assessment-management-toolbar" onSubmit={(event) => { event.preventDefault(); setFilters({ ...filters, q: search.trim(), offset: 0 }); }}><label className="resource-search">Search assessments<input type="search" maxLength={200} value={search} onChange={(event) => setSearch(event.target.value)} /></label><label>Status<select value={filters.status} onChange={(event) => setFilters({ ...filters, status: event.target.value as AssessmentStatus | "all", offset: 0 })}><option value="all">All current statuses</option><option value="planned">Planned</option><option value="completed">Completed</option><option value="cancelled">Cancelled</option><option value="archived">Archived</option></select></label><button className="secondary-button" disabled={assessments.loading}>Search</button></form></FilterPanel><p className="resource-note">{timezone ? `Dates use ${timezone}.` : "Loading your profile timezone before displaying dates or creating an assessment."} Archived definitions retain their result history.</p><LoadNotice hasData={context.data != null} loading={context.loading} error={context.error} retry={context.retry} /><LoadNotice label="Loading assessments…" hasData={assessments.data != null} loading={assessments.loading} error={assessments.error} retry={assessments.retry} />{assessments.data && <>{assessments.data.filters !== filters && <p className="resource-note">Showing the last loaded assessments while the selected filters resolve.</p>}{!assessments.data.assessments.length ? <div className="resource-empty"><h2>No assessments match this view</h2><p>Create an assessment or adjust the status and search filters.</p></div> : <ResponsiveView desktop={() => <AssessmentDesktopView groups={groups} timezone={timezone} />} mobile={() => <AssessmentMobileView groups={groups} timezone={timezone} />} />}<Pagination offset={assessments.data.filters.offset} total={assessments.data.total} busy={assessments.loading} change={(offset) => setFilters({ ...filters, offset })} /></>}{creating && timezone && <AssessmentEditor timezone={timezone} close={() => setCreating(false)} saved={(assessment) => router.push(`/assessments/${assessment.id}`)} />}</>;
}
