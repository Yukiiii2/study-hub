"use client";

import { useEffect, useRef } from "react";
import { useDialogDismiss } from "@/components/ui-motion";
import { AssistantPanelHeader } from "./assistant-panel-header";
import { AssistantPanelContent } from "./assistant-panel-content";
import type { assistantPageContext } from "./page-context";

/** Intentionally non-modal: the reader can use/navigate the underlying workspace. */
export function DesktopAssistantPanel({ page, close }: { page: ReturnType<typeof assistantPageContext>; close: () => void }) {
  const dialog = useRef<HTMLDialogElement>(null);
  const dismiss = useDialogDismiss(dialog, close);
  const dismissRef = useRef(dismiss);
  dismissRef.current = dismiss;
  useEffect(() => {
    const element = dialog.current;
    element?.show();
    element?.querySelector<HTMLElement>("h2")?.focus();
    const escape = (event: KeyboardEvent) => {
      if (event.key === "Escape" && !document.querySelector("dialog:modal")) { event.preventDefault(); dismissRef.current(); }
    };
    window.addEventListener("keydown", escape);
    return () => { window.removeEventListener("keydown", escape); element?.close(); };
  }, []);
  return <dialog ref={dialog} className="planner-dialog windowed-assistant desktop-assistant-panel" aria-modal="false" aria-labelledby="windowed-assistant-title"><AssistantPanelHeader context={page.label} close={dismiss} /><AssistantPanelContent page={page} /></dialog>;
}
