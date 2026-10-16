"use client";

import { useState, type ReactNode } from "react";
import { usePresentationMode } from "./responsive-view";

/** Small shared disclosure, not a second form/tree. Opening never remounts controls. */
export function FilterPanel({ children, label = "Search & filters" }: { children: ReactNode; label?: string }) {
  const mode = usePresentationMode();
  const [expanded, setExpanded] = useState(false);
  return <details className="filter-panel" open={mode === "desktop" || expanded} onToggle={event => {
    if (mode === "mobile") setExpanded(event.currentTarget.open);
  }}><summary>{label}</summary>{children}</details>;
}
