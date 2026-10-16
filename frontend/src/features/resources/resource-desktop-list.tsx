import Link from "next/link";
import type { Resource } from "@/services/resources";
import { StatusBadge } from "@/components/study-ui";
import { resourceDate, resourceSize, resourceStatus } from "./resource-format";
export type ResourceRowsProps = { resources: Resource[]; timezone: string };
export function ResourceDesktopList({ resources, timezone }: ResourceRowsProps) { return <><div className="resource-column-headings" aria-hidden="true"><span>Source / subject</span><span>Type / size</span><span>Status / uploaded</span></div><ul className="resource-list" aria-label="Resources">{resources.map((resource) => <li key={resource.id}><Link href={`/library/${resource.id}`} className="resource-row" data-subject={resource.subject_code ?? undefined}>
      <div className="resource-copy"><strong>{resource.title}</strong><span>{resource.original_filename}</span><span>{resource.subject_code ?? "No subject"}{resource.topic_title ? ` / ${resource.topic_title}` : ""}</span></div>
      <div className="resource-facts"><span className="resource-file-facts"><span className="resource-type-badge">{resource.resource_type.toUpperCase()}</span><span>{resourceSize(resource.file_size_bytes)}</span></span><span>{resource.page_count !== null ? `${resource.page_count} pages` : resource.row_count !== null ? `${resource.row_count} rows` : ""}</span></div>
      <div className="resource-state"><StatusBadge tone={resource.processing_status === "ready" ? "success" : resource.processing_status === "failed" ? "danger" : resource.processing_status === "processing" ? "info" : "neutral"}>{resourceStatus(resource)}</StatusBadge><time dateTime={resource.created_at}>{resourceDate(resource.created_at, timezone)}</time></div>
    </Link></li>)}</ul></>; }
