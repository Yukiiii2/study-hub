"use client";

import { useState } from "react";
import { assessmentError, createAttempt, updateAttempt, type AssessmentAttempt } from "@/services/assessments";
import { QuizDialog } from "@/features/quizzes/shared";
import { assessmentLocal, attemptInput, type AttemptFields } from "./form-state";

export function AttemptEditor({ assessmentId, attempt, timezone, close, saved }: { assessmentId: string; attempt?: AssessmentAttempt; timezone: string; close: () => void; saved: () => void }) {
  const [fields, setFields] = useState<AttemptFields>(() => ({ started: assessmentLocal(attempt?.started_at, timezone), completed: assessmentLocal(attempt?.completed_at, timezone), score: attempt?.score?.toString() ?? "", maximum: attempt?.max_score?.toString() ?? "", notes: attempt?.notes ?? "" }));
  const [busy, setBusy] = useState(false), [error, setError] = useState<string | null>(null);
  const change = (key: keyof AttemptFields, value: string) => setFields((current) => ({ ...current, [key]: value }));
  async function save() {
    setBusy(true); setError(null);
    try { const body = attemptInput(fields, timezone, attempt); if (attempt) await updateAttempt(attempt.id, body); else await createAttempt(assessmentId, body); saved(); close(); }
    catch (failure) { setError(assessmentError(failure)); } finally { setBusy(false); }
  }
  return <QuizDialog title={attempt ? "Edit result" : "Record result"} busy={busy} close={close}><p className="resource-note">Manually record this attempt. Leave both score fields blank for an unscored result. Saving a result does not change the assessment status.</p><form onSubmit={(event) => { event.preventDefault(); void save(); }}><fieldset disabled={busy} className="planner-form-grid"><label>Started (optional)<input autoFocus type="datetime-local" value={fields.started} onChange={(event) => change("started", event.target.value)} /></label><label>Completed (required when scored)<input type="datetime-local" required={fields.score.trim() !== "" || fields.maximum.trim() !== ""} value={fields.completed} onChange={(event) => change("completed", event.target.value)} /></label><label>Score (optional)<input type="number" min={0} step="any" value={fields.score} onChange={(event) => change("score", event.target.value)} /></label><label>Maximum score (optional)<input type="number" min={0} step="any" value={fields.maximum} onChange={(event) => change("maximum", event.target.value)} /></label><label className="planner-wide">Notes (optional)<textarea rows={4} maxLength={5000} value={fields.notes} onChange={(event) => change("notes", event.target.value)} /></label><p className="resource-note planner-wide">Dates use {timezone}. A scored result requires a positive maximum; its percentage is calculated when saved.</p></fieldset>{error && <p role="alert" className="auth-error">{error}</p>}<div className="planner-dialog-actions"><button className="primary-button" disabled={busy}>{busy ? "Saving…" : "Save result"}</button></div></form></QuizDialog>;
}
