"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { deleteResource, getResource, getResourceContent, getResourceLink, resourceError, resourceProcessingError, type Resource, type ResourceContent } from "@/services/resources";
import { ResourceContentView, ResourceError, ResourcePagination, resourceDate, resourceSize, resourceStatus } from "./resource-views";
import { useResourceTimezone } from "./use-resource-timezone";

export function ResourceDetail({ resourceId }: { resourceId: string }) {
  const router = useRouter();
  const [savedResource, setResource] = useState<Resource | null>(null);
  const resource = savedResource?.id === resourceId ? savedResource : null;
  const [error, setError] = useState<string | null>(null);
  const [retry, setRetry] = useState(0);
  const [loading, setLoading] = useState(true);
  const [content, setContent] = useState<{ data: ResourceContent; offset: number } | null>(null);
  const [contentError, setContentError] = useState<string | null>(null);
  const [contentLoading, setContentLoading] = useState(false);
  const [contentRetry, setContentRetry] = useState(0);
  const [offset, setOffset] = useState(0);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [busy, setBusy] = useState<"open" | "download" | "delete" | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const { timezone, timezoneNote, timezoneFailed, retryTimezone } = useResourceTimezone();
  useEffect(() => {
    setResource(null); setContent(null); setOffset(0); setContentError(null); setContentLoading(false);
    setConfirmDelete(false); setActionError(null); setBusy(null);
  }, [resourceId]);
  useEffect(() => {
    const controller = new AbortController(); setLoading(true); setError(null);
    void getResource(resourceId, controller.signal).then((data) => { if (!controller.signal.aborted) setResource(data); }).catch((error) => { if (!controller.signal.aborted) setError(resourceError(error)); }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [resourceId, retry]);
  useEffect(() => {
    if (!resource || resource.processing_status !== "ready") return;
    const controller = new AbortController(); setContentLoading(true); setContentError(null);
    void getResourceContent(resource.id, offset, controller.signal).then((data) => { if (!controller.signal.aborted) setContent({ data, offset }); }).catch((error) => { if (!controller.signal.aborted) setContentError(resourceError(error)); }).finally(() => { if (!controller.signal.aborted) setContentLoading(false); });
    return () => controller.abort();
  }, [resource, offset, contentRetry]);
  async function accessFile(download: boolean) {
    // Open in the click handler so browser popup rules do not block the async request.
    const target = window.open("", "_blank");
    if (!target) { setActionError("Allow this site's popups, then try opening the file again."); return; }
    target.opener = null; setBusy(download ? "download" : "open"); setActionError(null);
    try {
      const link = await getResourceLink(resourceId, download);
      const url = new URL(link.url);
      if (!["https:", "http:"].includes(url.protocol)) throw new Error("Invalid file link");
      target.location.replace(url.href);
    } catch (error) { target.close(); setActionError(resourceError(error)); }
    finally { setBusy(null); }
  }
  async function remove() {
    setBusy("delete"); setActionError(null);
    try { await deleteResource(resourceId); router.push("/library"); }
    catch (error) { setActionError(resourceError(error)); setBusy(null); }
  }
  return <>
    <Link href="/library" className="back-link">Back to Library</Link>
    {error && <ResourceError message={error} retry={() => setRetry((value) => value + 1)} />}
    {loading && <p className="resource-note" role="status">{resource ? "Refreshing resource…" : "Loading resource…"}</p>}
    {resource && <>
      <header className="page-heading"><h1 className="resource-title">{resource.title}</h1><p>{resource.original_filename}</p></header>
      <div className="resource-actions"><button type="button" className="primary-button" disabled={!!busy} onClick={() => void accessFile(true)}>{busy === "download" ? "Preparing download…" : "Download original"}</button>{resource.resource_type === "pdf" && <button type="button" className="secondary-button" disabled={!!busy} onClick={() => void accessFile(false)}>{busy === "open" ? "Opening…" : "Open PDF"}</button>}<button type="button" className="secondary-button planner-danger" disabled={!!busy} onClick={() => { setConfirmDelete(true); setActionError(null); }}>Delete resource</button></div>
      <p className="resource-note">File links are private and expire after 2 minutes.</p>
      {resource.resource_type === "pdf" && resource.processing_status === "ready" && <nav className="assistant-shortcuts" aria-label="AI study assistance for this resource"><Link href={`/assistant?${new URLSearchParams({ resource_id: resource.id, mode: "ask" })}`}>Ask about this PDF</Link><Link href={`/assistant?${new URLSearchParams({ resource_id: resource.id, mode: "quiz" })}`}>Generate question drafts</Link><Link href={`/assistant?${new URLSearchParams({ resource_id: resource.id, mode: "cards" })}`}>Generate flashcard drafts</Link></nav>}
      {actionError && <p role="alert" className="auth-error">{actionError}</p>}
      {confirmDelete && <div className="planner-delete-confirm"><p>Delete this resource, its original file and extracted text? This cannot be undone.</p><button type="button" className="secondary-button planner-danger" disabled={!!busy} onClick={() => void remove()}>{busy === "delete" ? "Deleting…" : "Confirm deletion"}</button><button type="button" className="secondary-button" disabled={!!busy} onClick={() => setConfirmDelete(false)}>Keep resource</button></div>}
      <dl className="resource-metadata"><div><dt>Type</dt><dd>{resource.resource_type.toUpperCase()}</dd></div><div><dt>Size</dt><dd>{resourceSize(resource.file_size_bytes)}</dd></div><div><dt>Subject</dt><dd>{resource.subject_code ?? "No subject"}</dd></div><div><dt>Topic</dt><dd>{resource.topic_title ?? "No topic"}</dd></div><div><dt>Processing</dt><dd>{resourceStatus(resource)}</dd></div>{resource.page_count !== null && <div><dt>Pages</dt><dd>{resource.page_count}</dd></div>}{resource.row_count !== null && <div><dt>Rows</dt><dd>{resource.row_count}</dd></div>}<div><dt>Uploaded</dt><dd><time dateTime={resource.created_at}>{resourceDate(resource.created_at, timezone)}</time></dd></div><div><dt>Updated</dt><dd><time dateTime={resource.updated_at}>{resourceDate(resource.updated_at, timezone)}</time></dd></div></dl>
      <div className="resource-timezone"><p className="resource-note">{timezoneNote}</p>{timezoneFailed && <button type="button" className="secondary-button" onClick={retryTimezone}>Retry timezone</button>}</div>
      {resource.processing_status === "failed" && <section className="curriculum-state"><h2>PDF processing failed</h2><p>{resourceProcessingError(resource)}</p><p>Download or open the original to review it.</p></section>}
      {(resource.processing_status === "uploaded" || resource.processing_status === "processing") && <section className="curriculum-state"><h2>Text is not ready yet</h2><p>The original file is available. Refresh to check its processing status.</p><button type="button" className="secondary-button" disabled={loading} onClick={() => setRetry((value) => value + 1)}>Refresh status</button></section>}
      {contentError && <ResourceError message={contentError} retry={() => setContentRetry((value) => value + 1)} />}
      {contentLoading && <p className="resource-note" role="status">{content ? "Updating preview…" : "Loading preview…"}</p>}
      {content && content.data.resource.id === resourceId && resource.processing_status === "ready" && <><ResourceContentView data={content.data} />{resource.resource_type === "pdf" && <ResourcePagination offset={content.offset} limit={10} total={content.data.total_sections} busy={contentLoading || !!contentError} changePage={setOffset} />}</>}
    </>}
  </>;
}
