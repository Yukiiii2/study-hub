"use client";

import { useCallback, useEffect, useState } from "react";
import { getDecks, type Deck } from "@/services/flashcards";
import { LoadNotice, useQuizLoad } from "@/features/quizzes/shared";

export function DeckSelector({ value, change, disabled = false, filter = false }: { value: string; change: (id: string, deck?: Deck) => void; disabled?: boolean; filter?: boolean }) {
  const [offset, setOffset] = useState(0);
  const [options, setOptions] = useState<Deck[]>([]);
  const loaded = useQuizLoad(useCallback((signal) => getDecks({ limit: 100, offset }, signal), [offset]));
  useEffect(() => { if (loaded.data) setOptions((current) => [...current.filter((deck) => !loaded.data!.decks.some((next) => next.id === deck.id)), ...loaded.data!.decks]); }, [loaded.data]);
  return <div className="flashcard-deck-selector"><label>{filter ? "Deck" : "Deck (optional)"}<select value={value} disabled={disabled || !loaded.data} onChange={(event) => change(event.target.value, options.find((deck) => deck.id === event.target.value))}><option value="">{filter ? "All decks" : "No deck"}</option>{value && !options.some((deck) => deck.id === value) && <option value={value}>Current deck</option>}{options.map((deck) => <option key={deck.id} value={deck.id}>{deck.title}</option>)}</select></label><LoadNotice loading={false} error={loaded.error} retry={loaded.retry} />{loaded.data && offset + 100 < loaded.data.total && <button type="button" className="secondary-button" disabled={disabled || loaded.loading} onClick={() => setOffset(offset + 100)}>Load more decks</button>}</div>;
}
