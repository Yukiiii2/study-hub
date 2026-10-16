import Link from "next/link";
import type { ResourceRowsProps } from "./resource-desktop-list";
import { StatusBadge } from "@/components/study-ui";
import { resourceDate, resourceSize, resourceStatus } from "./resource-format";

export function ResourceMobileList({ resources, timezone }: ResourceRowsProps) {
  return <ul className="mobile-resource-list" aria-label="Resources">{resources.map(resource => <li key={resource.id}><Link className="mobile-resource-row" href={`/library/${resource.id}`} data-subject={resource.subject_code ?? undefined}>
    <div className="mobile-resource-title"><span className="resource-type-badge">{resource.resource_type.toUpperCase()}</span><strong>{resource.title}</strong></div><span className="mobile-resource-filename">{resource.original_filename}</span>
    <span className="mobile-resource-context">{resource.subject_code ?? "No subject"}{resource.topic_title && ` · ${resource.topic_title}`}</span>
    <div className="mobile-resource-meta"><StatusBadge tone={resource.processing_status === "ready" ? "success" : resource.processing_status === "failed" ? "danger" : "info"}>{resourceStatus(resource)}</StatusBadge><span>{resourceSize(resource.file_size_bytes)}{resource.page_count !== null ? ` · ${resource.page_count} pages` : resource.row_count !== null ? ` · ${resource.row_count} rows` : ""}</span></div><time dateTime={resource.created_at}>{resourceDate(resource.created_at,timezone)}</time>
  </Link></li>)}</ul>;
}
