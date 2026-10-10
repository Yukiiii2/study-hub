"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { createCard, getDeck, updateCard, flashcardError, type Card, type CardInput, type CardStatus } from "@/services/flashcards";
import { Associations, LoadNotice, QuizDialog, SourceFields, useQuizLoad } from "@/features/quizzes/shared";
import { DeckSelector } from "./deck-selector";
import { aiCardSaveOutcomeUnknown } from "@/features/assistant/draft-save";

export function CardEditor({ card, initial, close, saved, uncertain }: { card?: Card; initial?: Partial<CardInput>; close: () => void; saved: (card: Card) => void; uncertain?: () => void }) {
  const seed = card ?? initial;
  const receipt = card ? undefined : initial?.ai_draft_receipt;
  const saveLock = useRef(false);
  const outcomeUnknown = useRef(false);
  const [front, setFront] = useState(seed?.front ?? "");
  const [back, setBack] = useState(seed?.back ?? "");
  const [notes, setNotes] = useState(seed?.notes ?? "");
  const [deck, setDeck] = useState(seed?.deck_id ?? "");
  const [deckSubject, setDeckSubject] = useState<string | null>(null);
  const [subject, setSubject] = useState(seed?.subject_id ?? "");
  const [topic, setTopic] = useState(seed?.topic_id ?? "");
  const [resource, setResource] = useState(seed?.resource_id ?? "");
  const [page, setPage] = useState(seed?.source_page?.toString() ?? "");
  const [status, setStatus] = useState<CardStatus>(seed?.status ?? "active");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saveUncertain, setSaveUncertain] = useState(false);
  const deckState = useQuizLoad(useCallback((signal) => deck ? getDeck(deck, signal) : Promise.resolve(null), [deck]));
  useEffect(() => {
    if (deckState.data?.id !== deck) return;
    const forcedSubject = deckState.data.subject_id;
    setDeckSubject(forcedSubject);
    if (forcedSubject && forcedSubject !== subject) { setSubject(forcedSubject); setTopic(""); }
  }, [deckState.data, deck, subject]);
  async function save() {
    if (saveLock.current || outcomeUnknown.current) return;
    if (!front.trim() || !back.trim()) { setError("Enter text for both the front and back."); return; }
    if (deck && (deckState.loading || deckState.error || deckState.data?.id !== deck)) { setError("Load the selected deck before saving."); return; }
    if (deckSubject && subject !== deckSubject) { setError("The card subject must match its deck."); return; }
    const body: CardInput = { front: front.trim(), back: back.trim(), notes: notes.trim() || null, deck_id: deck || null, subject_id: subject || null, topic_id: topic || null, resource_id: resource || null, source_page: page ? Number(page) : null, status: receipt ? "suspended" : status };
    if (receipt) body.ai_draft_receipt = receipt;
    saveLock.current = true; setBusy(true); setError(null);
    try { const result = card ? await updateCard(card.id, body) : await createCard(body); saved(result); close(); }
    catch (failure) {
      if (receipt && aiCardSaveOutcomeUnknown(failure)) {
        outcomeUnknown.current = true; setSaveUncertain(true); uncertain?.();
        setError("Save confirmation was lost. This card may already be in Flashcards. Check Flashcards before creating another draft.");
      } else setError(flashcardError(failure));
    } finally { saveLock.current = false; setBusy(false); }
  }
  return <QuizDialog title={card ? "Edit flashcard" : receipt ? "Review AI flashcard" : "New flashcard"} close={close} busy={busy}><p className="resource-note">{card ? "Content changes preserve the schedule. Archived cards retain their review history." : receipt ? "Review the card and source before confirming. AI cards save suspended. Activate them in Flashcards after review to include them in Recall." : "New active cards are due immediately after saving."}</p><form className="study-editor" onSubmit={(event) => { event.preventDefault(); void save(); }}><fieldset disabled={busy} className="planner-form-grid"><label className="planner-wide">Front<textarea autoFocus required rows={4} maxLength={5000} value={front} onChange={(event) => setFront(event.target.value)} /></label><label className="planner-wide">Back<textarea required rows={5} maxLength={12000} value={back} onChange={(event) => setBack(event.target.value)} /></label><label className="planner-wide">Notes (optional)<textarea rows={2} maxLength={5000} value={notes} onChange={(event) => setNotes(event.target.value)} /></label><DeckSelector value={deck} disabled={busy} change={(id, selected) => { setDeck(id); setDeckSubject(selected?.subject_id ?? null); if (selected?.subject_id && selected.subject_id !== subject) { setSubject(selected.subject_id); setTopic(""); } }} /><label>Status<select disabled={!!receipt} value={receipt ? "suspended" : status} onChange={(event) => setStatus(event.target.value as CardStatus)}><option value="active">Active</option><option value="suspended">Suspended</option>{card?.status === "archived" && <option value="archived">Archived</option>}</select></label>{deck && <div className="planner-wide"><LoadNotice loading={deckState.loading} error={deckState.error} retry={deckState.retry} /></div>}{deckSubject && <p className="resource-note planner-wide">This deck requires its assigned subject. Choose another deck to change the card subject.</p>}<Associations subject={subject} topic={topic} disabled={busy} changeSubject={(id) => { if (deckSubject && id !== deckSubject) { setError("This deck requires its assigned subject. Choose another deck first."); return; } setSubject(id); }} changeTopic={setTopic} /><SourceFields resource={resource} page={page} changeResource={setResource} changePage={setPage} disabled={busy} /></fieldset>{error && <p className="auth-error" role="alert">{error}</p>}<div className="planner-dialog-actions"><button className="primary-button" disabled={busy || saveUncertain || !!deck && (deckState.loading || !!deckState.error || deckState.data?.id !== deck)}>{busy ? "Saving…" : receipt ? "Confirm and save flashcard" : "Save flashcard"}</button></div></form></QuizDialog>;
}
