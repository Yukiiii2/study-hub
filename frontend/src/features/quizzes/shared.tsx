"use client";

import { useCallback, useEffect, useRef, useState, type ReactNode } from "react";
import { getSubjects, getSubjectTopics, type Subject, type Topic } from "@/services/subjects";
import { getResources, type Resource } from "@/services/resources";
import { quizError } from "@/services/quizzes";

export function useQuizLoad<T>(loader: (signal: AbortSignal) => Promise<T>) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [revision, setRevision] = useState(0);
  useEffect(() => { const controller = new AbortController(); setLoading(true); setError(null);
    void loader(controller.signal).then((next) => { if (!controller.signal.aborted) setData(next); }).catch((failure) => { if (!controller.signal.aborted) setError(quizError(failure)); }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [loader, revision]);
  return { data, setData, loading, error, retry: () => setRevision((value) => value + 1) };
}
export function LoadNotice({ loading, error, retry }: { loading: boolean; error: string | null; retry: () => void }) {
  return <>{loading && <p className="resource-note" role="status">Loading study data…</p>}{error && <div className="resource-error"><p className="auth-error" role="alert">{error}</p><button type="button" className="secondary-button" onClick={retry}>Try again</button></div>}</>;
}
export function Pagination({ offset, total, change, busy = false }: { offset: number; total: number; change: (offset: number) => void; busy?: boolean }) {
  return <div className="resource-pagination"><span>{total ? `${offset + 1}–${Math.min(offset + 20, total)} of ${total}` : "0 results"}</span><button type="button" className="secondary-button" disabled={busy || !offset} onClick={() => change(Math.max(0, offset - 20))}>Previous</button><button type="button" className="secondary-button" disabled={busy || offset + 20 >= total} onClick={() => change(offset + 20)}>Next</button></div>;
}
export function QuizDialog({ title, close, busy = false, children }: { title: string; close: () => void; busy?: boolean; children: ReactNode }) {
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => { const element = dialog.current; element?.showModal(); return () => element?.close(); }, []);
  return <dialog ref={dialog} className="planner-dialog quiz-dialog" aria-label={title} onCancel={(event) => { event.preventDefault(); if (!busy) close(); }}><div className="planner-dialog-heading"><h2>{title}</h2><button type="button" className="secondary-button" disabled={busy} onClick={close}>Close</button></div>{children}</dialog>;
}
export function Associations({ subject, topic, changeSubject, changeTopic, disabled = false }: { subject: string; topic: string; changeSubject: (id: string) => void; changeTopic: (id: string) => void; disabled?: boolean }) {
  const subjects = useQuizLoad<Subject[]>(useCallback((signal) => getSubjects(signal), []));
  const topics = useQuizLoad<Topic[]>(useCallback((signal) => subject ? getSubjectTopics(subject, signal) : Promise.resolve([]), [subject]));
  const currentTopics = topics.data?.filter((item) => item.subject_id === subject) ?? [];
  return <><label>Subject (optional)<select disabled={disabled || subjects.loading || !subjects.data} value={subject} onChange={(event) => { changeSubject(event.target.value); changeTopic(""); }}><option value="">No subject</option>{subjects.data?.map((item) => <option key={item.id} value={item.id}>{item.code} — {item.name}</option>)}</select></label><label>Topic (optional)<select disabled={disabled || !subject || topics.loading || !!topics.error} value={topic} onChange={(event) => changeTopic(event.target.value)}><option value="">No topic</option>{currentTopics.map((item) => <option key={item.id} value={item.id}>{item.code ? `${item.code} — ` : ""}{item.title}</option>)}</select></label><div className="planner-wide"><LoadNotice loading={false} error={subjects.error} retry={subjects.retry} /><LoadNotice loading={false} error={topics.error} retry={topics.retry} /></div></>;
}
export function SourceFields({ resource, page, changeResource, changePage, disabled }: { resource: string; page: string; changeResource: (id: string) => void; changePage: (page: string) => void; disabled?: boolean }) {
  const [offset, setOffset] = useState(0);
  const [options, setOptions] = useState<Resource[]>([]);
  const resources = useQuizLoad(useCallback((signal) => getResources({ limit: 100, offset }, signal), [offset]));
  useEffect(() => { if (resources.data) setOptions((current) => [...current.filter((item) => !resources.data!.resources.some((next) => next.id === item.id)), ...resources.data!.resources]); }, [resources.data]);
  const selected = options.find((item) => item.id === resource);
  return <><label>Source resource (optional)<select disabled={disabled || !resources.data} value={resource} onChange={(event) => { changeResource(event.target.value); changePage(""); }}><option value="">No source</option>{resource && !selected && <option value={resource}>Current source</option>}{options.map((item) => <option value={item.id} key={item.id}>{item.title} ({item.resource_type.toUpperCase()})</option>)}</select></label><label>PDF page (optional)<input type="number" min={1} max={selected?.page_count ?? 200} disabled={disabled || selected?.resource_type !== "pdf"} value={page} onChange={(event) => changePage(event.target.value)} /></label><div className="planner-wide"><LoadNotice loading={resources.loading} error={resources.error} retry={resources.retry} />{resources.data && offset + 100 < resources.data.total && <button type="button" className="secondary-button" disabled={resources.loading || disabled} onClick={() => setOffset(offset + 100)}>Load more sources</button>}</div></>;
}
