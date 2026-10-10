import type { ReactNode } from "react";

/** Shared heading hierarchy without owning a page's actions or data. */
export function PageHeader({ title, description, meta, actions, titleId, className = "" }: {
  title: string;
  description: string;
  meta?: ReactNode;
  actions?: ReactNode;
  titleId?: string;
  className?: string;
}) {
  return <header className={`page-heading page-header ${className}`}>
    <div className="page-header-copy"><h1 id={titleId}>{title}</h1><p>{description}</p>{meta && <div className="page-header-meta">{meta}</div>}</div>
    {actions && <div className="page-header-actions">{actions}</div>}
  </header>;
}
