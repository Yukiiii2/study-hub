"use client";

import { useEffect, useRef, useState } from "react";
import { aiError, explainAIAnswer, type AIAnswer } from "@/services/ai";
import { AIResponseView } from "./response-view";

export function ExplainAnswerAction({ attemptId, questionId }: { attemptId: string; questionId: string }) {
  const [response, setResponse] = useState<AIAnswer | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const controller = useRef<AbortController | null>(null);
  useEffect(() => () => controller.current?.abort(), []);
  async function explain() {
    if (controller.current) return;
    const request = new AbortController(); controller.current = request; setBusy(true); setError(null);
    try { const result = await explainAIAnswer({ attempt_id: attemptId, question_id: questionId }, request.signal); if (!request.signal.aborted) setResponse(result); }
    catch (failure) { if (!request.signal.aborted) setError(aiError(failure)); }
    finally { if (!request.signal.aborted) { controller.current = null; setBusy(false); } }
  }
  return <div className="assistant-review-action"><button type="button" className="secondary-button" disabled={busy} onClick={() => void explain()}>{busy ? "Explaining…" : response ? "Explain again with AI" : "Explain this answer with AI"}</button>{error && <p className="auth-error" role="alert">{error}</p>}{response && <AIResponseView response={response} />}</div>;
}
