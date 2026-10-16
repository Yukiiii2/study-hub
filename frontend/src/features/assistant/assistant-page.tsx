"use client";

import { PageHeader } from "@/components/page-header";
import { PendingLabel } from "@/components/study-ui";
import { useEffect, useRef } from "react";
import { AssistantContextFields } from "./assistant-context-fields";
import type { AIDifficulty, AIMode } from "@/services/ai";
import { AIDraftPreview } from "./draft-preview";
import { AssistantConversation } from "./assistant-conversation";
import { useAssistant } from "./assistant-provider";
import type { AssistantController, AssistantInitial } from "./use-assistant-controller";
export { useAssistantController } from "./use-assistant-controller";
export type { AssistantInitial } from "./use-assistant-controller";

export function AssistantPage({ initial = {} }: { initial?: AssistantInitial }) {
  return <AssistantWorkspace initial={initial} />;
}
export function AssistantWorkspace({ initial }: { initial: AssistantInitial }) {
  const assistant = useAssistant();
  const signature = JSON.stringify(initial);
  const applied = useRef("");
  useEffect(() => {
    assistant.activate();
    if (Object.values(initial).some(Boolean) && applied.current !== signature) {
      applied.current = signature;
      assistant.controller.applyInitial(initial);
    }
  }, [signature]); // Explicit source links initialize once; Expand keeps the shared conversation.
  return <AssistantWorkspaceView controller={assistant.controller} />;
}

export function AssistantWorkspaceView({ controller }: { controller: AssistantController }) {
  const { resource, mode, setMode, prompt, setPrompt, count, setCount, difficulty, setDifficulty, setSnapshot,
    preview, previewRevision, busy, selected, pendingLabel, resourceReady, clearPreview, generate } = controller;
  return <><PageHeader title="Study assistant" description="Ask about a source, or prepare a few study drafts to review and save." />
    <div className="assistant-workspace"><form aria-label="Study context and request" className="assistant-form" onSubmit={(event) => { event.preventDefault(); void generate(); }}><h2>Choose study context</h2><p className="resource-note">Ground your request in a subject, topic or private PDF.</p><fieldset disabled={busy} className="planner-form-grid">
      <AssistantContextFields controller={controller} />
      <label className="planner-wide">Study task<select value={mode} onChange={(event) => { clearPreview(); const next = event.target.value as AIMode; setMode(next); setCount(next === "cards" ? 5 : 3); if (next !== "cards") setSnapshot(null); }}><option value="ask">Ask or summarize</option><option value="quiz">Generate question drafts</option><option value="cards">Generate flashcard drafts</option></select></label>
      <label className="planner-wide">{mode === "ask" ? "Question or summary request" : "Instructions (optional)"}<textarea required={mode === "ask"} maxLength={2000} rows={4} value={prompt} onChange={(event) => setPrompt(event.target.value)} /><span className="resource-note">{prompt.length}/2000 characters</span></label>
      {mode !== "ask" && <label>Number of drafts<input required type="number" min={1} max={mode === "quiz" ? 5 : 10} value={count} onChange={(event) => setCount(Number(event.target.value))} /></label>}
      {mode === "quiz" && <label>Difficulty<select value={difficulty} onChange={(event) => setDifficulty(event.target.value as AIDifficulty)}><option value="basic">Basic</option><option value="intermediate">Intermediate</option><option value="advanced">Advanced</option></select></label>}
    </fieldset><p className="resource-note">Changing the task or context clears the preview. Generating again replaces unsaved drafts after a successful response. Your conversation stays available while signed in, including in the windowed assistant. It is cleared when you sign out or reload.</p>
      <button className="primary-button" aria-busy={busy} disabled={busy || !resourceReady || !!resource && (selected.loading || !!selected.error)}><PendingLabel pending={busy} idle={mode === "ask" ? "Ask assistant" : "Generate preview"} busy={pendingLabel} /></button>
    </form>
    <div className="assistant-output" aria-label="Study assistant results">
    <AssistantConversation controller={controller} />
    {preview && <AIDraftPreview key={previewRevision} response={preview} disabled={busy} />}
    </div></div>
  </>;
}
