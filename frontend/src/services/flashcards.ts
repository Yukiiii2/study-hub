import { ApiError, authenticatedDelete, authenticatedGet, authenticatedPatch, authenticatedPost } from "./api";
import type { AIProvenance } from "./ai-provenance";

export type CardStatus = "active" | "suspended" | "archived";
export type Rating = "again" | "hard" | "good" | "easy";
export type DeckInput = { title: string; description: string | null; subject_id: string | null };
export type Deck = DeckInput & { id: string; is_archived: boolean; created_at: string; updated_at: string };
export type CardInput = { deck_id: string | null; subject_id: string | null; topic_id: string | null; resource_id: string | null; source_page: number | null; front: string; back: string; notes: string | null; status: CardStatus; ai_draft_receipt?: string };
export type Card = Omit<CardInput, "ai_draft_receipt"> & { id: string; ai_provenance?: AIProvenance | null; interval_days: number; next_review_at: string; review_revision: number; created_at: string; updated_at: string };
export type ReviewInput = { rating: Rating; expected_revision: number; request_id: string };
export type CardReview = { id: string; flashcard_id: string; request_id: string; previous_revision: number; reviewed_at: string; rating: Rating; previous_interval_days: number; next_interval_days: number; next_review_at: string; algorithm_version: string; front_snapshot: string; back_snapshot: string; created_at: string };
export type CardList = { cards: Card[]; total: number };
export type DeckList = { decks: Deck[]; total: number };
export type ReviewList = { reviews: CardReview[]; total: number };
export type QueueMode = "due" | "overdue" | "today" | "upcoming";
export type DueSummary = { overdue: number; due_today: number; upcoming: number };
export type DueQueue = CardList & { summary: DueSummary; timezone: string; as_of: string };
export type FlashcardFilters = { subject_id?: string; topic_id?: string; resource_id?: string; deck_id?: string; status?: CardStatus | "all"; q?: string; mode?: QueueMode; offset?: number; limit?: number };
const cardPath = (id: string) => `/api/flashcards/${encodeURIComponent(id)}`;
const deckPath = (id: string) => `/api/flashcard-decks/${encodeURIComponent(id)}`;
function query(filters: FlashcardFilters) { const params = new URLSearchParams(); for (const [key, value] of Object.entries(filters)) if (value !== "" && value !== undefined) params.set(key, String(value)); return `?${params}`; }
export const getCards = (filters: FlashcardFilters, signal?: AbortSignal) => authenticatedGet<CardList>(`/api/flashcards${query(filters)}`, signal);
export const getCard = (id: string, signal?: AbortSignal) => authenticatedGet<Card>(cardPath(id), signal);
export const createCard = (body: CardInput) => authenticatedPost<Card>("/api/flashcards", body);
export const updateCard = (id: string, body: Partial<CardInput>) => authenticatedPatch<Card>(cardPath(id), body);
export const archiveCard = (id: string) => authenticatedDelete(cardPath(id));
export const getDecks = (filters: Pick<FlashcardFilters, "subject_id" | "q" | "offset" | "limit">, signal?: AbortSignal) => authenticatedGet<DeckList>(`/api/flashcard-decks${query(filters)}`, signal);
export const getDeck = (id: string, signal?: AbortSignal) => authenticatedGet<Deck>(deckPath(id), signal);
export const createDeck = (body: DeckInput) => authenticatedPost<Deck>("/api/flashcard-decks", body);
export const updateDeck = (id: string, body: Partial<DeckInput>) => authenticatedPatch<Deck>(deckPath(id), body);
export const archiveDeck = (id: string) => authenticatedDelete(deckPath(id));
export const getDueCards = (filters: Pick<FlashcardFilters, "mode" | "subject_id" | "deck_id" | "offset" | "limit">, signal?: AbortSignal) => authenticatedGet<DueQueue>(`/api/flashcards/due${query(filters)}`, signal);
export const reviewCard = (id: string, body: ReviewInput) => authenticatedPost<CardReview>(`${cardPath(id)}/review`, body);
export const getCardReviews = (id: string, offset = 0, signal?: AbortSignal) => authenticatedGet<ReviewList>(`${cardPath(id)}/reviews?limit=20&offset=${offset}`, signal);
export function flashcardError(error: unknown) {
  if (error instanceof ApiError) {
    if (error.status === 404) return "This card or deck is no longer available. Refresh and try again.";
    if (error.status === 409) return "This card or deck has changed, is not due, or has conflicting associations. Refresh before trying a new action.";
    if (error.status === 422) return "Check the required text and deck, subject, topic and source selections.";
    return error.message;
  }
  return "The flashcard request failed. Try again.";
}
