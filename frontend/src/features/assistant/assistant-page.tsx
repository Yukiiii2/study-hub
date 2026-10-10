"use client";

import { PageHeader } from "@/components/page-header";
import { LoadingNotice } from "@/components/study-ui";
import { useCallback, useEffect, useRef, useState } from "react";
import { useAuth } from "@/features/auth/auth-provider";
import { Associations, LoadNotice, useQuizLoad } from "@/features/quizzes/shared";
import { getResource, getResources, type Resource } from "@/services/resources";
import { aiError, askAI, generateAICards, generateAIQuestions, type AIContext, type AIDifficulty, type AIMode, type AIResult, type AICards, type AIQuestions, type SnapshotContext } from "@/services/ai";
import { AIRequestGate, retainDraftPreview, validContextId } from "./draft-state";
import { AIDraftPreview } from "./draft-preview";
import { AIResponseView } from "./response-view";

export type AssistantInitial = { subject_id?: string; topic_id?: string; resource_id?: string; attempt_id?: string; question_id?: string; mode?: string; prompt?: string };
export function AssistantPage({ initial = {} }: { initial?: AssistantInitial }) {
  const { user } = useAuth();
  // The shared layout owns authentication. Remount private, transient previews on identity/context changes.
  return <AssistantWorkspace key={`${user?.id ?? ""}:${JSON.stringify(initial)}`} initial={initial} />;
}

export function AssistantWorkspace({ initial }: { initial: AssistantInitial }) {
  const [subject, setSubject] = useState(validContextId(initial.subject_id));
  const [topic, setTopic] = useState(validContextId(initial.topic_id));
  const [resource, setResource] = useState(validContextId(initial.resource_id));
  const [mode, setMode] = useState<AIMode>(initial.mode === "quiz" || initial.mode === "cards" ? initial.mode : "ask");
  const [prompt, setPrompt] = useState((initial.prompt ?? "").slice(0, 2000));
  const [count, setCount] = useState(initial.mode === "cards" ? 5 : 3);
  const [difficulty, setDifficulty] = useState<AIDifficulty>("intermediate");
  const [snapshot, setSnapshot] = useState<SnapshotContext | null>(() => {
    const attempt = validContextId(initial.attempt_id), question = validContextId(initial.question_id);
    return attempt && question ? { attempt_id: attempt, question_id: question } : null;
  });
  const [offset, setOffset] = useState(0);
  const [result, setResult] = useState<AIResult | null>(null);
  const [preview, setPreview] = useState<AIQuestions | AICards | null>(null);
  const [previewRevision, setPreviewRevision] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const gate = useRef(new AIRequestGate());
  const controller = useRef<AbortController | null>(null);
  const resources = useQuizLoad(useCallback((signal) => getResources({ limit: 20, offset, resource_type: "pdf", subject_id: subject || undefined }, signal), [offset, subject]));
  const selected = useQuizLoad(useCallback((signal) => resource ? getResource(resource, signal) : Promise.resolve(null), [resource]));
  const ready = resources.data?.resources.filter((item) => item.resource_type === "pdf" && item.processing_status === "ready") ?? [];
  const selectedResource = selected.data?.id === resource ? selected.data : null;
  const resourceReady = !resource || !!selectedResource && selectedResource.resource_type === "pdf" && selectedResource.processing_status === "ready";
  useEffect(() => () => { controller.current?.abort(); gate.current.invalidate(); }, []);
  function clearPreview() { controller.current?.abort(); gate.current.invalidate(); setBusy(false); setResult(null); setPreview(null); setError(null); }
  function selectResource(id: string) {
    clearPreview(); setResource(id);
    const source: Resource | undefined = ready.find((item) => item.id === id);
    if (source?.subject_id) { setSubject(source.subject_id); setTopic(source.topic_id ?? ""); }
    else if (source?.topic_id) setTopic(source.topic_id);
  }
  async function generate() {
    if (mode === "ask" && !prompt.trim()) { setError("Enter a study question or a summary request."); return; }
    if (resource && !resourceReady) { setError("Choose a ready text PDF or clear the resource selection."); return; }
    if ((initial.attempt_id || initial.question_id) && !snapshot && mode === "cards" && !subject && !topic && !resource) { setError("This quiz mistake link is incomplete. Return to the completed quiz review."); return; }
    const ticket = gate.current.begin(); if (ticket === null) return;
    const request = new AbortController(); controller.current = request; setBusy(true); setError(null);
    const context: AIContext = snapshot && mode === "cards" ? {} : { subject_id: subject || null, topic_id: topic || null, resource_id: resource || null };
    try {
      const response = mode === "ask" ? await askAI({ ...context, prompt: prompt.trim() }, request.signal)
        : mode === "quiz" ? await generateAIQuestions({ ...context, prompt: prompt.trim() || undefined, count, difficulty }, request.signal)
        : await generateAICards({ ...context, ...(snapshot ?? {}), prompt: prompt.trim() || undefined, count }, request.signal);
      if (request.signal.aborted || !gate.current.current(ticket)) return;
      setResult(response);
      setPreview((previous) => retainDraftPreview(previous, response));
      if (("questions" in response && response.questions.length || "cards" in response && response.cards.length) && !response.insufficient_context) setPreviewRevision((current) => current + 1);
    } catch (failure) { if (!request.signal.aborted && gate.current.current(ticket)) setError(aiError(failure)); }
    finally { if (gate.current.current(ticket)) { gate.current.finish(ticket); controller.current = null; setBusy(false); } }
  }
  return <><PageHeader title="Study assistant" description="Ask about a source, or prepare a few study drafts to review and save." />
    <div className="assistant-workspace"><form className="assistant-form" onSubmit={(event) => { event.preventDefault(); void generate(); }}><fieldset disabled={busy} className="planner-form-grid">
      <label className="planner-wide">Study task<select value={mode} onChange={(event) => { clearPreview(); const next = event.target.value as AIMode; setMode(next); setCount(next === "cards" ? 5 : 3); if (next !== "cards") setSnapshot(null); }}><option value="ask">Ask or summarize</option><option value="quiz">Generate question drafts</option><option value="cards">Generate flashcard drafts</option></select></label>
      {snapshot ? <div className="planner-wide"><p className="resource-note">Using the saved completed quiz mistake. The service checks the original answer and source.</p><button type="button" className="secondary-button" onClick={() => { clearPreview(); setSnapshot(null); }}>Choose other study context</button></div> : <>
        <Associations subject={subject} topic={topic} disabled={busy} changeSubject={(id) => { clearPreview(); setSubject(id); setResource(""); setOffset(0); }} changeTopic={(id) => { clearPreview(); setTopic(id); setResource(""); }} />
        <label className="planner-wide">Ready text PDF (optional)<select disabled={resources.loading || !!resources.error} value={resource} onChange={(event) => selectResource(event.target.value)}><option value="">Use subject or topic context</option>{resource && !ready.some((item) => item.id === resource) && <option value={resource}>{selectedResource?.title ?? "Selected resource"}</option>}{ready.map((item) => <option key={item.id} value={item.id}>{item.title}</option>)}</select></label>
        <div className="planner-wide"><LoadNotice loading={resources.loading} error={resources.error} retry={resources.retry} />{resource && <><LoadNotice loading={selected.loading} error={selected.error} retry={selected.retry} /><button type="button" className="secondary-button" onClick={() => selectResource("")}>Clear PDF selection</button></>}{resource && !selected.loading && !selected.error && !resourceReady && <p className="auth-error" role="alert">This resource does not have ready PDF text. Choose another source.</p>}
          {resources.data && <div className="resource-pagination"><span className="resource-note">Ready PDFs on this source page: {ready.length}</span><button type="button" className="secondary-button" disabled={!offset || resources.loading} onClick={() => setOffset(Math.max(0, offset - 20))}>Previous sources</button><button type="button" className="secondary-button" disabled={offset + 20 >= resources.data.total || resources.loading} onClick={() => setOffset(offset + 20)}>Next sources</button></div>}
        </div></>}
      <label className="planner-wide">{mode === "ask" ? "Question or summary request" : "Instructions (optional)"}<textarea required={mode === "ask"} maxLength={2000} rows={4} value={prompt} onChange={(event) => setPrompt(event.target.value)} /><span className="resource-note">{prompt.length}/2000 characters</span></label>
      {mode !== "ask" && <label>Number of drafts<input required type="number" min={1} max={mode === "quiz" ? 5 : 10} value={count} onChange={(event) => setCount(Number(event.target.value))} /></label>}
      {mode === "quiz" && <label>Difficulty<select value={difficulty} onChange={(event) => setDifficulty(event.target.value as AIDifficulty)}><option value="basic">Basic</option><option value="intermediate">Intermediate</option><option value="advanced">Advanced</option></select></label>}
    </fieldset><p className="resource-note">Changing the task or context clears the preview. Generating again replaces unsaved drafts after a successful response. Nothing is kept after you leave this page.</p>
      <button className="primary-button" disabled={busy || !resourceReady || !!resource && (selected.loading || !!selected.error)}>{busy ? "Preparing response…" : mode === "ask" ? "Ask assistant" : "Generate preview"}</button>
    </form>
    <div className="assistant-output" aria-label="Study assistant results">{busy && <LoadingNotice>Preparing AI study assistance. This can take up to 30 seconds.</LoadingNotice>}
    {error && <p className="auth-error" role="alert">{error}</p>}
    {result && ("answer" in result || result.insufficient_context || !preview) && <AIResponseView response={result} />}
    {preview && <AIDraftPreview key={previewRevision} response={preview} disabled={busy} />}
    {!result && !preview && <section className="assistant-welcome"><h2>Study with your sources</h2><p>Choose a subject, topic or ready PDF to begin. Topic context uses AI knowledge; source-backed responses include quotes and page references.</p><dl><div><dt>Ask or summarize</dt><dd>Clarify a concept or review source material.</dd></div><div><dt>Prepare study drafts</dt><dd>Review and edit every question or card before saving.</dd></div></dl></section>}
    </div></div>
  </>;
}
