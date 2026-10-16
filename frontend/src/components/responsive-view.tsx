"use client";

import { useSyncExternalStore, type ReactNode } from "react";
import { ContentSkeleton, type SkeletonLayout } from "./study-ui";

type Mode = "mobile" | "desktop" | null;
const listeners = new Set<() => void>();
let query: MediaQueryList | undefined;
const media = () => query ??= window.matchMedia("(max-width: 959px)");
const notify = () => listeners.forEach(listener => listener());
function subscribe(listener: () => void) {
  if (!listeners.size) media().addEventListener("change", notify);
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
    if (!listeners.size) media().removeEventListener("change", notify);
  };
}
const clientSnapshot = (): Mode => media().matches ? "mobile" : "desktop";
const serverSnapshot = (): Mode => null;

/** Data stays in the parent. SSR/first hydration agree; only one layout mounts. */
export function usePresentationMode() {
  return useSyncExternalStore(subscribe, clientSnapshot, serverSnapshot);
}
export function ResponsiveView({ mobile, desktop, layout = "rows" }: {
  mobile: () => ReactNode; desktop: () => ReactNode; layout?: SkeletonLayout;
}) {
  const mode = usePresentationMode();
  return mode === null ? <ContentSkeleton label="Preparing workspace…" layout={layout} /> : mode === "mobile" ? mobile() : desktop();
}
