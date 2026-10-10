"use client";

import { useEffect, useState } from "react";
import { getSubjects, type Subject } from "@/services/subjects";
import { getResources, resourceError, type ResourceList } from "@/services/resources";
import { ResourceError, ResourceListView } from "./resource-views";
import { UploadDialog } from "./upload-dialog";
import { useResourceTimezone } from "./use-resource-timezone";
import { PageHeader } from "@/components/page-header";
import { InterfaceIcon } from "@/components/interface-icon";

const limit = 20;
export function ResourceLibrary() {
  const [subjects, setSubjects] = useState<Subject[] | null>(null);
  const [subjectError, setSubjectError] = useState(false);
  const [subjectRetry, setSubjectRetry] = useState(0);
  const [filters, setFilters] = useState({ subject_id: "", resource_type: "", q: "", offset: 0 });
  const [search, setSearch] = useState("");
  const [loaded, setLoaded] = useState<{ data: ResourceList; filters: typeof filters } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retry, setRetry] = useState(0);
  const [upload, setUpload] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const { timezone, timezoneNote, timezoneFailed, retryTimezone } = useResourceTimezone();
  useEffect(() => {
    const controller = new AbortController(); setSubjectError(false);
    void getSubjects(controller.signal).then((data) => { if (!controller.signal.aborted) setSubjects(data); }).catch(() => { if (!controller.signal.aborted) setSubjectError(true); });
    return () => controller.abort();
  }, [subjectRetry]);
  useEffect(() => {
    const controller = new AbortController(); setLoading(true); setError(null);
    void getResources({ ...filters, limit }, controller.signal).then((data) => { if (!controller.signal.aborted) setLoaded({ data, filters }); }).catch((error) => { if (!controller.signal.aborted) setError(resourceError(error)); }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [filters, retry]);
  const shownFilters = loaded?.filters ?? filters;
  return <>
    <PageHeader title="Library" description="Your study sources, organized by subject and topic." className="resource-heading" actions={<button type="button" className="primary-button" disabled={!subjects} onClick={() => { setNotice(null); setUpload(true); }}><InterfaceIcon name="plus" />Upload resource</button>} />
    {notice && <p className="planner-notice" role="status">{notice}</p>}
    {subjectError && <ResourceError message="Could not load subjects. Retry to upload or filter by subject." retry={() => setSubjectRetry((value) => value + 1)} />}
    <form className="resource-filters ui-panel" aria-label="Find resources" onSubmit={(event) => { event.preventDefault(); setFilters((current) => ({ ...current, q: search.trim(), offset: 0 })); }}>
      <label className="resource-search">Search<input type="search" maxLength={200} value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Title or filename" /></label>
      <label>Type<select value={filters.resource_type} onChange={(event) => setFilters((current) => ({ ...current, resource_type: event.target.value, offset: 0 }))}><option value="">All types</option><option value="pdf">PDF</option><option value="csv">CSV</option></select></label>
      <label>Subject<select disabled={!subjects} value={filters.subject_id} onChange={(event) => setFilters((current) => ({ ...current, subject_id: event.target.value, offset: 0 }))}><option value="">All subjects</option>{subjects?.map((subject) => <option key={subject.id} value={subject.id}>{subject.code}</option>)}</select></label><button className="secondary-button">Search</button>
    </form>
    <div className="resource-timezone"><p className="resource-note">{timezoneNote}</p>{timezoneFailed && <button type="button" className="secondary-button" onClick={retryTimezone}>Retry timezone</button>}</div>
    {loaded && loaded.filters !== filters && <p className="resource-note">Showing the last loaded results while the selected filters are refreshed.</p>}
    <ResourceListView data={loaded?.data ?? null} loading={loading} error={error} retry={() => setRetry((value) => value + 1)} offset={shownFilters.offset} limit={limit} changePage={(offset) => setFilters((current) => ({ ...current, offset }))} timezone={timezone} filtered={!!(shownFilters.q || shownFilters.subject_id || shownFilters.resource_type)} />
    {upload && subjects && <UploadDialog subjects={subjects} close={() => setUpload(false)} saved={(resource) => { setNotice(resource.processing_status === "failed" ? "File uploaded. PDF processing failed; open the resource for details." : "Resource uploaded."); setFilters((current) => ({ ...current, offset: 0 })); setRetry((value) => value + 1); }} />}
  </>;
}
