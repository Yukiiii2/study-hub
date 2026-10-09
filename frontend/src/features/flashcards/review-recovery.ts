import type { Rating, ReviewInput } from "@/services/flashcards";
import type { PendingReview } from "./review-state";

export type ReviewMetadata = ReviewInput & { card_id: string };
type ReviewStorage = Pick<Storage, "getItem" | "setItem" | "removeItem">;
const key = (ownerId: string) => `study-hub:recall-review:${encodeURIComponent(ownerId)}`;
const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
function valid(value: unknown): value is ReviewMetadata {
  if (!value || typeof value !== "object" || Array.isArray(value)) return false;
  const entry = value as ReviewMetadata;
  return Object.keys(entry).length === 4 && Object.keys(entry).every((field) => ["card_id", "expected_revision", "rating", "request_id"].includes(field))
    && typeof entry.card_id === "string" && uuid.test(entry.card_id) && typeof entry.request_id === "string" && uuid.test(entry.request_id)
    && Number.isSafeInteger(entry.expected_revision) && entry.expected_revision >= 0 && entry.expected_revision <= 2147483647
    && (["again", "hard", "good", "easy"] as Rating[]).includes(entry.rating);
}
export function reviewStorage(): ReviewStorage | null { try { return window.sessionStorage; } catch { return null; } }
export function clearReviewRecovery(storage: ReviewStorage | null, ownerId: string) { try { storage?.removeItem(key(ownerId)); } catch { /* Keep server confirmations independent of browser storage. */ } }
export function rememberReview(storage: ReviewStorage | null, ownerId: string, pending: PendingReview): boolean {
  const entry: ReviewMetadata = { card_id: pending.card.id, ...pending.body };
  if (!storage || !ownerId || !valid(entry)) return false;
  try { storage.setItem(key(ownerId), JSON.stringify(entry)); return true; } catch { return false; }
}
export function readReviewRecovery(storage: ReviewStorage | null, ownerId: string): { metadata: ReviewMetadata | null; available: boolean } {
  if (!storage || !ownerId) return { metadata: null, available: false };
  try {
    const raw = storage.getItem(key(ownerId));
    if (!raw) return { metadata: null, available: true };
    let entry: unknown;
    try { entry = raw.length <= 512 ? JSON.parse(raw) : null; } catch { entry = null; }
    if (!valid(entry)) { clearReviewRecovery(storage, ownerId); return { metadata: null, available: true }; }
    return { metadata: entry, available: true };
  } catch { return { metadata: null, available: false }; }
}
