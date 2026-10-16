import { ResponsiveView } from "@/components/responsive-view";
import { ResourceDesktopList } from "./resource-desktop-list";
import { ResourceMobileList } from "./resource-mobile-list";
import Link from "next/link";
import type { Resource, ResourceContent, ResourceList } from "@/services/resources";
import { ContentSkeleton, LoadingNotice, SectionHeader, StatusBadge } from "@/components/study-ui";

import { resourceStatus, resourceSize, resourceDate } from "./resource-format";
export { resourceStatus, resourceSize, resourceDate } from "./resource-format";

export function ResourceError({ message, retry }: { message: string; retry: () => void }) {
  return <div className="resource-error ui-panel"><p className="auth-error" role="alert">{message}</p><button type="button" className="secondary-button" onClick={retry}>Retry</button></div>;
}
export function ResourcePagination({ offset, limit, total, busy, changePage }: { offset: number; limit: number; total: number; busy: boolean; changePage: (offset: number) => void }) {
  if (total === 0 && offset === 0) return null;
  return <nav className="resource-pagination" aria-label="Resource pagination"><span>{total ? `${offset + 1}–${Math.min(offset + limit, total)} of ${total}` : "0 resources"}</span><button type="button" className="secondary-button" disabled={busy || offset === 0} onClick={() => changePage(Math.max(0, offset - limit))}>Previous</button><button type="button" className="secondary-button" disabled={busy || offset + limit >= total} onClick={() => changePage(offset + limit)}>Next</button></nav>;
}
export function ResourceListView({ data, loading, error, retry, offset, limit, changePage, timezone, filtered = false }: { data: ResourceList | null; loading: boolean; error: string | null; retry: () => void; offset: number; limit: number; changePage: (offset: number) => void; timezone: string; filtered?: boolean }) {
  return <>
    {error && <ResourceError message={error} retry={retry} />}
    {loading && (data ? <LoadingNotice>Refreshing resources…</LoadingNotice> : <ContentSkeleton label="Loading resources…" />)}
    {data && <><div className="resource-list-heading"><SectionHeader title={filtered ? "Matching resources" : "Study resources"} detail={`${data.total} ${data.total === 1 ? "resource" : "resources"}`} /></div>{data.resources.length === 0 ? <section className="curriculum-state"><h2>{filtered ? "No matching resources" : "No resources yet"}</h2><p>{filtered ? "Try another search or filter." : "Upload a text-based PDF or CSV to keep your study sources here."}</p></section> : <><ResponsiveView desktop={() => <ResourceDesktopList resources={data.resources} timezone={timezone} />} mobile={() => <ResourceMobileList resources={data.resources} timezone={timezone} />} /></>}<ResourcePagination offset={offset} limit={limit} total={data.total} busy={loading || !!error} changePage={changePage} /></>}
  </>;
}
export function ResourceContentView({ data }: { data: ResourceContent }) {
  if (data.resource.resource_type === "csv") return <section className="resource-content" aria-labelledby="resource-preview-title"><SectionHeader title="CSV preview" titleId="resource-preview-title" detail={`Showing ${data.rows.length} of ${data.row_count ?? data.rows.length} rows. The original file is available to download.`} /><div className="resource-table-scroll" role="region" aria-label="CSV preview" tabIndex={0}><table><thead><tr>{data.headers.map((header, index) => <th scope="col" key={index}>{header}</th>)}</tr></thead><tbody>{data.rows.map((row, index) => <tr key={index}>{row.map((cell, column) => <td key={column}>{cell}</td>)}</tr>)}</tbody></table></div></section>;
  return <section className="resource-content" aria-labelledby="resource-preview-title"><SectionHeader title="Extracted text" titleId="resource-preview-title" />{data.sections.length === 0 ? <p className="resource-note">No extracted text is available.</p> : data.sections.map((section) => <article key={section.id} className="resource-page"><header className="resource-page-heading"><h3>Page {section.page_number}</h3></header><p>{section.content || "No text on this page."}</p></article>)}</section>;
}
