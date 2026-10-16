"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useQuizLoad } from "@/features/quizzes/shared";
import { getResource, getResources, type Resource } from "@/services/resources";
import { aiError, askAI, generateAICards, generateAIQuestions, type AIContext, type AIDifficulty, type AIMode, type AIResult, type AICards, type AIQuestions, type SnapshotContext } from "@/services/ai";
import { AIRequestGate, retainDraftPreview, validContextId } from "./draft-state";

export type AssistantInitial = { subject_id?: string; topic_id?: string; resource_id?: string; attempt_id?: string; question_id?: string; mode?: string; prompt?: string };
export type AssistantTurn = { id: number; prompt: string; response: AIResult };

/** One request owner; session-memory only. The existing API remains stateless. */
export function useAssistantController(initial: AssistantInitial = {}, enabled = true) {
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
  const [invalidSnapshot, setInvalidSnapshot] = useState(!!(initial.attempt_id || initial.question_id) && !(validContextId(initial.attempt_id) && validContextId(initial.question_id)));
  const [offset, setOffset] = useState(0);
  const [result, setResult] = useState<AIResult | null>(null);
  const [preview, setPreview] = useState<AIQuestions | AICards | null>(null);
  const [previewRevision, setPreviewRevision] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [turns, setTurns] = useState<AssistantTurn[]>([]);
  const [pendingPrompt, setPendingPrompt] = useState("");
  const turnSequence = useRef(0);
  const gate = useRef(new AIRequestGate());
  const controller = useRef<AbortController | null>(null);
  const resources = useQuizLoad(useCallback((signal) => enabled ? getResources({ limit: 20, offset, resource_type: "pdf", subject_id: subject || undefined }, signal) : Promise.resolve(null), [enabled, offset, subject]));
  const selected = useQuizLoad(useCallback((signal) => enabled && resource ? getResource(resource, signal) : Promise.resolve(null), [enabled, resource]));
  const ready = resources.data?.resources.filter((item) => item.resource_type === "pdf" && item.processing_status === "ready") ?? [];
  const selectedResource = selected.data?.id === resource ? selected.data : null;
  const pendingLabel = mode === "ask" ? "Generating answer…" : mode === "quiz" ? "Creating quiz draft…" : "Creating flashcards…";
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
    if (invalidSnapshot && !snapshot && mode === "cards" && !subject && !topic && !resource) { setError("This quiz mistake link is incomplete. Return to the completed quiz review."); return; }
    const ticket = gate.current.begin(); if (ticket === null) return;
    const request = new AbortController(); controller.current = request; setBusy(true); setError(null); setPendingPrompt(prompt.trim() || (mode === "quiz" ? "Generate question drafts" : "Generate flashcard drafts"));
    const context: AIContext = snapshot && mode === "cards" ? {} : { subject_id: subject || null, topic_id: topic || null, resource_id: resource || null };
    try {
      const response = mode === "ask" ? await askAI({ ...context, prompt: prompt.trim() }, request.signal)
        : mode === "quiz" ? await generateAIQuestions({ ...context, prompt: prompt.trim() || undefined, count, difficulty }, request.signal)
        : await generateAICards({ ...context, ...(snapshot ?? {}), prompt: prompt.trim() || undefined, count }, request.signal);
      if (request.signal.aborted || !gate.current.current(ticket)) return;
      setResult(response);
      const id = ++turnSequence.current;
      setTurns((previous) => [...previous, { id, prompt: prompt.trim() || (mode === "quiz" ? "Generate question drafts" : "Generate flashcard drafts"), response }].slice(-20));
      setPreview((previous) => retainDraftPreview(previous, response));
      if (("questions" in response && response.questions.length || "cards" in response && response.cards.length) && !response.insufficient_context) setPreviewRevision((current) => current + 1);
    } catch (failure) { if (!request.signal.aborted && gate.current.current(ticket)) setError(aiError(failure)); }
    finally { if (gate.current.current(ticket)) { gate.current.finish(ticket); controller.current = null; setBusy(false); } }
  }
  function applyInitial(next: AssistantInitial) {
    clearPreview(); setSubject(validContextId(next.subject_id)); setTopic(validContextId(next.topic_id)); setResource(validContextId(next.resource_id));
    setMode(next.mode === "quiz" || next.mode === "cards" ? next.mode : "ask");
    setPrompt((next.prompt ?? "").slice(0, 2000)); setCount(next.mode === "cards" ? 5 : 3); setOffset(0);
    const attempt = validContextId(next.attempt_id), question = validContextId(next.question_id);
    setSnapshot(attempt && question ? { attempt_id: attempt, question_id: question } : null);
    setInvalidSnapshot(!!(next.attempt_id || next.question_id) && !(attempt && question));
  }
  function resetConversation() { clearPreview(); setTurns([]); setPendingPrompt(""); setPrompt(""); }
  return { subject, setSubject, topic, setTopic, resource, setResource, mode, setMode, prompt, setPrompt, count, setCount,
    difficulty, setDifficulty, snapshot, setSnapshot, offset, setOffset, result, preview, previewRevision, busy, error,
    resources, selected, ready, selectedResource, pendingLabel, resourceReady, clearPreview, selectResource, generate,
    turns, pendingPrompt, applyInitial, resetConversation };
}
export type AssistantController = ReturnType<typeof useAssistantController>;
