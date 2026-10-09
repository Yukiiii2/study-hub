"use client";

import { useEffect, useRef, useState } from "react";
import { getSubjectTopics, type Subject, type Topic } from "@/services/subjects";
import { resourceError, uploadFileError, uploadResource, type Resource } from "@/services/resources";

export function UploadDialog({ subjects, close, saved }: { subjects: Subject[]; close: () => void; saved: (resource: Resource) => void }) {
  const dialog = useRef<HTMLDialogElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [subject, setSubject] = useState("");
  const [topic, setTopic] = useState("");
  const [topicState, setTopicState] = useState<{ subject: string; topics: Topic[]; error: boolean } | null>(null);
  const [topicRetry, setTopicRetry] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { const element = dialog.current; element?.showModal(); return () => element?.close(); }, []);
  useEffect(() => {
    if (!subject) return;
    const controller = new AbortController(); setTopicState(null);
    void getSubjectTopics(subject, controller.signal).then((topics) => { if (!controller.signal.aborted) setTopicState({ subject, topics, error: false }); }).catch(() => { if (!controller.signal.aborted) setTopicState({ subject, topics: [], error: true }); });
    return () => controller.abort();
  }, [subject, topicRetry]);
  const current = topicState?.subject === subject ? topicState : null;
  const loadingTopics = !!subject && !current;
  const topicError = !!subject && !!current?.error;
  async function upload() {
    if (!file) { setError("Choose a PDF or CSV file."); return; }
    const failure = uploadFileError(file);
    if (failure) { setError(failure); return; }
    if (topic && !current?.topics.some((value) => value.id === topic && value.subject_id === subject)) { setError("Choose a topic that belongs to the selected subject."); return; }
    setBusy(true); setError(null);
    try { const resource = await uploadResource(file, title, subject, topic); saved(resource); close(); }
    catch (error) { setError(resourceError(error)); }
    finally { setBusy(false); }
  }
  return <dialog ref={dialog} className="planner-dialog resource-upload" aria-labelledby="resource-upload-title" onCancel={(event) => { event.preventDefault(); if (!busy) close(); }}>
    <div className="planner-dialog-heading"><h2 id="resource-upload-title">Upload resource</h2><button type="button" className="secondary-button" onClick={close} disabled={busy}>Close</button></div>
    <p className="resource-note">Text-based PDF or CSV, up to 4 MiB. Scanned PDFs cannot be processed.</p>
    <form onSubmit={(event) => { event.preventDefault(); void upload(); }}><fieldset disabled={busy} className="planner-form-grid">
      <label className="planner-wide">File<input autoFocus required type="file" accept=".pdf,.csv,application/pdf,text/csv" onChange={(event) => { const next = event.target.files?.[0] ?? null; setFile(next); setError(next ? uploadFileError(next) : null); }} /></label>
      <label className="planner-wide">Title (optional)<input maxLength={200} value={title} onChange={(event) => setTitle(event.target.value)} /></label>
      <label>Subject (optional)<select value={subject} onChange={(event) => { setSubject(event.target.value); setTopic(""); }}><option value="">No subject</option>{subjects.map((value) => <option key={value.id} value={value.id}>{value.code} — {value.name}</option>)}</select></label>
      <label>Topic (optional)<select value={topic} disabled={!subject || loadingTopics || topicError} onChange={(event) => setTopic(event.target.value)}><option value="">{loadingTopics ? "Loading topics…" : "No topic"}</option>{current?.topics.map((value) => <option key={value.id} value={value.id}>{value.code ? `${value.code} — ` : ""}{value.title}</option>)}</select></label>
      {topicError && <div className="planner-field-error"><p role="alert" className="auth-error">Could not load topics. Retry before uploading.</p><button type="button" className="secondary-button" onClick={() => setTopicRetry((value) => value + 1)}>Retry topics</button></div>}
    </fieldset>{error && <p className="auth-error" role="alert">{error}</p>}<div className="planner-dialog-actions"><button className="primary-button" disabled={busy || loadingTopics || topicError}>{busy ? "Uploading…" : "Upload resource"}</button></div></form>
  </dialog>;
}
