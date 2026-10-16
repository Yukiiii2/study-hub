"use client";

import { useEffect, useRef } from "react";
import { useDialogDismiss } from "@/components/ui-motion";
import { AssistantPanelHeader } from "./assistant-panel-header";
import { AssistantPanelContent } from "./assistant-panel-content";
import type { assistantPageContext } from "./page-context";

/** Native modal owns focus/inertness; visualViewport keeps the composer above the keyboard. */
export function MobileAssistantSheet({ page, close }: { page: ReturnType<typeof assistantPageContext>; close: () => void }) {
  const dialog = useRef<HTMLDialogElement>(null);
  const dismiss = useDialogDismiss(dialog, close);
  useEffect(() => {
    const element = dialog.current;
    const viewport = window.visualViewport;
    const fit = () => {
      element?.style.setProperty("--assistant-viewport-height", `${viewport?.height ?? window.innerHeight}px`);
      element?.style.setProperty("--assistant-keyboard-offset", `${Math.max(0, window.innerHeight - (viewport?.height ?? window.innerHeight) - (viewport?.offsetTop ?? 0))}px`);
    };
    fit(); element?.showModal(); element?.querySelector<HTMLElement>("h2")?.focus();
    viewport?.addEventListener("resize", fit); viewport?.addEventListener("scroll", fit);
    return () => { viewport?.removeEventListener("resize", fit); viewport?.removeEventListener("scroll", fit); element?.close(); };
  }, []);
  return <dialog ref={dialog} className="planner-dialog windowed-assistant mobile-assistant-sheet" aria-labelledby="windowed-assistant-title" onCancel={event => { event.preventDefault(); dismiss(); }}><div className="assistant-sheet-handle" aria-hidden="true" /><AssistantPanelHeader context={page.label} close={dismiss} /><AssistantPanelContent page={page} /></dialog>;
}
