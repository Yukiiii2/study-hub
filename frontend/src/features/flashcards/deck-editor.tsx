"use client";

import { useCallback, useState } from "react";
import { getSubjects } from "@/services/subjects";
import { createDeck, updateDeck, flashcardError, type Deck } from "@/services/flashcards";
import { LoadNotice, QuizDialog, useQuizLoad } from "@/features/quizzes/shared";

export function DeckEditor({ deck, close, saved }: { deck?: Deck; close: () => void; saved: (deck: Deck) => void }) {
  const [title, setTitle] = useState(deck?.title ?? "");
  const [description, setDescription] = useState(deck?.description ?? "");
  const [subject, setSubject] = useState(deck?.subject_id ?? "");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const subjects = useQuizLoad(useCallback((signal) => getSubjects(signal), []));
  async function save() { setBusy(true); setError(null); const body = { title: title.trim(), description: description.trim() || null, subject_id: subject || null }; try { const result = deck ? await updateDeck(deck.id, body) : await createDeck(body); saved(result); close(); } catch (failure) { setError(flashcardError(failure)); } finally { setBusy(false); } }
  return <QuizDialog title={deck ? "Edit deck" : "New deck"} busy={busy} close={close}><p className="resource-note">A subject-specific deck accepts only cards with that subject. Changing the subject will fail if assigned cards conflict.</p><form className="study-editor" onSubmit={(event) => { event.preventDefault(); void save(); }}><fieldset className="planner-form-grid" disabled={busy}><label className="planner-wide">Title<input autoFocus required maxLength={200} value={title} onChange={(event) => setTitle(event.target.value)} /></label><label className="planner-wide">Description (optional)<textarea rows={3} maxLength={2000} value={description} onChange={(event) => setDescription(event.target.value)} /></label><label className="planner-wide">Subject (optional)<select value={subject} disabled={!subjects.data} onChange={(event) => setSubject(event.target.value)}><option value="">Any subject</option>{subjects.data?.map((item) => <option key={item.id} value={item.id}>{item.code} — {item.name}</option>)}</select></label></fieldset><LoadNotice loading={subjects.loading} error={subjects.error} retry={subjects.retry} />{error && <p className="auth-error" role="alert">{error}</p>}<div className="planner-dialog-actions"><button className="primary-button" disabled={busy}>{busy ? "Saving…" : "Save deck"}</button></div></form></QuizDialog>;
}
