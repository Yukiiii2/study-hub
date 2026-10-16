"use client";

import { useId } from "react";
import { PendingLabel } from "@/components/study-ui";
import type { AssistantController } from "./use-assistant-controller";

export function AssistantComposer({ controller }: { controller: AssistantController }) {
  const id = useId();
  return <form className="windowed-assistant-composer" onSubmit={event => { event.preventDefault(); void controller.generate(); }}>
    <label htmlFor={id}>{controller.mode === "ask" ? "Your study question" : "Draft instructions (optional)"}</label>
    <textarea id={id} data-assistant-composer rows={3} required={controller.mode === "ask"} maxLength={2000} value={controller.prompt} disabled={controller.busy} onChange={event => controller.setPrompt(event.target.value)} placeholder="Ask about your selected study context…" />
    <div><span className="resource-note">{controller.prompt.length}/2000</span><button type="submit" className="primary-button" disabled={controller.busy || !controller.resourceReady} aria-busy={controller.busy}><PendingLabel pending={controller.busy} idle={controller.mode === "ask" ? "Send" : "Generate draft"} busy={controller.pendingLabel} /></button></div>
  </form>;
}
