"use client";

import Link from "next/link";
import { useEffect, useRef } from "react";
import { AssistantConversation } from "./assistant-conversation";
import { AssistantComposer } from "./assistant-composer";
import { AssistantContextFields } from "./assistant-context-fields";
import { useAssistant } from "./assistant-provider";
import type { assistantPageContext } from "./page-context";

export function AssistantPanelContent({ page }: { page: ReturnType<typeof assistantPageContext> }) {
  const { controller } = useAssistant();
  const scroll = useRef<HTMLDivElement>(null);
  const follow = useRef(true);
  useEffect(() => {
    // Auto-follow only while the reader is already near the end.
    const element = scroll.current;
    if (element && follow.current) element.scrollTop = element.scrollHeight;
  }, [controller.turns.length, controller.busy, controller.error]);
  return <><div className="windowed-assistant-scroll" ref={scroll} onScroll={event => { const element = event.currentTarget; follow.current = element.scrollHeight - element.clientHeight - element.scrollTop < 120; }}>
    <details className="windowed-assistant-context"><summary>Study context{controller.resource ? " · PDF selected" : controller.subject ? " · Subject selected" : " · Choose a source"}</summary>
      <fieldset className="planner-form-grid" disabled={controller.busy}><AssistantContextFields controller={controller} />
        <label className="planner-wide">Study task<select value={controller.mode} onChange={event => { controller.clearPreview(); const next = event.target.value as "ask" | "quiz" | "cards"; controller.setMode(next); controller.setCount(next === "cards" ? 5 : 3); if (next !== "cards") controller.setSnapshot(null); }}><option value="ask">Ask or summarize</option><option value="quiz">Generate question drafts</option><option value="cards">Generate flashcard drafts</option></select></label>
        {controller.mode !== "ask" && <p className="resource-note planner-wide">Creates {controller.count} drafts. <Link href="/assistant" className="quiz-text-link">Expand</Link> to adjust count/difficulty, edit and confirm each save.</p>}
      </fieldset>
    </details>
    <AssistantConversation controller={controller} compact prompts={page.prompts} />
    {!!controller.turns.length && <button type="button" className="ghost-button assistant-clear" disabled={controller.busy} onClick={controller.resetConversation}>Clear conversation</button>}
  </div><AssistantComposer controller={controller} /></>;
}
