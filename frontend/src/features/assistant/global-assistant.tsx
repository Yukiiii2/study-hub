"use client";

import { useEffect, useRef } from "react";
import { usePathname } from "next/navigation";
import { InterfaceIcon } from "@/components/interface-icon";
import { usePresentationMode } from "@/components/responsive-view";
import { useAssistant } from "./assistant-provider";
import { assistantPageContext } from "./page-context";
import { DesktopAssistantPanel } from "./desktop-assistant-panel";
import { MobileAssistantSheet } from "./mobile-assistant-sheet";

export function GlobalAssistant() {
  const pathname = usePathname();
  const mode = usePresentationMode();
  const assistant = useAssistant();
  const trigger = useRef<HTMLButtonElement>(null);
  const page = assistantPageContext(pathname);
  const fullWorkspace = pathname === "/assistant";
  useEffect(() => { if (fullWorkspace) assistant.setOpen(false); }, [fullWorkspace, assistant.setOpen]);
  if (fullWorkspace || mode === null) return null;
  const close = () => { assistant.setOpen(false); requestAnimationFrame(() => trigger.current?.focus()); };
  return <div className="global-assistant-layer">
    <button ref={trigger} type="button" className="global-assistant-launcher" aria-label="Open Study Assistant" aria-haspopup="dialog" aria-expanded={assistant.open} hidden={assistant.open} onClick={() => {
      assistant.activate();
      if (!assistant.controller.busy && !assistant.controller.turns.length && !assistant.controller.prompt && (page.source.subject_id || page.source.resource_id)) assistant.controller.applyInitial({ subject_id: page.source.subject_id ?? undefined, resource_id: page.source.resource_id ?? undefined });
      assistant.setOpen(true);
    }}><InterfaceIcon name="assistant" /><span>Assistant</span></button>
    {assistant.open && (mode === "mobile" ? <MobileAssistantSheet page={page} close={close} /> : <DesktopAssistantPanel page={page} close={close} />)}
  </div>;
}
