import Link from "next/link";
import type { Resource, ResourceContent, ResourceList } from "@/services/resources";

export const resourceStatus = (resource: Resource) => ({ uploaded: "Uploaded", processing: "Processing", ready: "Ready", failed: "Processing failed" })[resource.processing_status];
export const resourceSize = (bytes: number) => bytes < 1024 ? `${bytes} bytes` : bytes < 1048576 ? `${(bytes / 1024).toFixed(1)} KiB` : `${(bytes / 1048576).toFixed(1)} MiB`;
export function resourceDate(value: string, timezone: string) { return new Intl.DateTimeFormat("en", { timeZone: timezone, month: "short", day: "numeric", year: "numeric" }).format(new Date(value)); }

export function ResourceError({ message, retry }: { message: string; retry: () => void }) {
  return <div className="resource-error"><p className="auth-error" role="alert">{message}</p><button type="button" className="secondary-button" onClick={retry}>Retry</button></div>;
}
export function ResourcePagination({ offset, limit, total, busy, changePage }: { offset: number; limit: number; total: number; busy: boolean; changePage: (offset: number) => void }) {
  return <nav className="resource-pagination" aria-label="Resource pagination"><span>{total ? `${offset + 1}–${Math.min(offset + limit, total)} of ${total}` : "0 resources"}</span><button type="button" className="secondary-button" disabled={busy || offset === 0} onClick={() => changePage(Math.max(0, offset - limit))}>Previous</button><button type="button" className="secondary-button" disabled={busy || offset + limit >= total} onClick={() => changePage(offset + limit)}>Next</button></nav>;
}
export function ResourceListView({ data, loading, error, retry, offset, limit, changePage, timezone, filtered = false }: { data: ResourceList | null; loading: boolean; error: string | null; retry: () => void; offset: number; limit: number; changePage: (offset: number) => void; timezone: string; filtered?: boolean }) {
  return <>
    {error && <ResourceError message={error} retry={retry} />}
    {loading && <p className="resource-note" role="status">{data ? "Updating resources…" : "Loading resources…"}</p>}
    {data && <>{data.resources.length === 0 ? <section className="curriculum-state"><h2>{filtered ? "No matching resources" : "No resources yet"}</h2><p>{filtered ? "Try another search or filter." : "Upload a text-based PDF or CSV to keep your study sources here."}</p></section> : <ul className="resource-list" aria-label="Resources">{data.resources.map((resource) => <li key={resource.id}><Link href={`/library/${resource.id}`} className="resource-row">
      <div className="resource-copy"><strong>{resource.title}</strong><span>{resource.original_filename}</span><span>{resource.subject_code ?? "No subject"}{resource.topic_title ? ` / ${resource.topic_title}` : ""}</span></div>
      <div className="resource-facts"><span>{resource.resource_type.toUpperCase()} / {resourceSize(resource.file_size_bytes)}</span><span>{resource.page_count !== null ? `${resource.page_count} pages` : resource.row_count !== null ? `${resource.row_count} rows` : ""}</span></div>
      <div className="resource-state"><span data-status={resource.processing_status}>{resourceStatus(resource)}</span><time dateTime={resource.created_at}>{resourceDate(resource.created_at, timezone)}</time></div>
    </Link></li>)}</ul>}<ResourcePagination offset={offset} limit={limit} total={data.total} busy={loading || !!error} changePage={changePage} /></>}
  </>;
}
export function ResourceContentView({ data }: { data: ResourceContent }) {
  if (data.resource.resource_type === "csv") return <section className="resource-content"><h2>CSV preview</h2><p className="resource-note">Showing {data.rows.length} of {data.row_count ?? data.rows.length} rows. The original file is available to download.</p><div className="resource-table-scroll" role="region" aria-label="CSV preview" tabIndex={0}><table><thead><tr>{data.headers.map((header, index) => <th scope="col" key={index}>{header}</th>)}</tr></thead><tbody>{data.rows.map((row, index) => <tr key={index}>{row.map((cell, column) => <td key={column}>{cell}</td>)}</tr>)}</tbody></table></div></section>;
  return <section className="resource-content"><h2>Extracted text</h2>{data.sections.length === 0 ? <p className="resource-note">No extracted text is available.</p> : data.sections.map((section) => <article key={section.id} className="resource-page"><h3>Page {section.page_number}</h3><p>{section.content || "No text on this page."}</p></article>)}</section>;
}
