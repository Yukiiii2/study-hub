"use client";

import { useCallback, useState } from "react";
import { getCardReviews, type Card, type CardReview } from "@/services/flashcards";
import { useResourceTimezone as useFlashcardTimezone } from "@/features/resources/use-resource-timezone";
import { LoadNotice, Pagination, QuizDialog, useQuizLoad } from "@/features/quizzes/shared";
import { flashcardTimestamp, ratingLabel } from "./review-state";

export function CardHistoryView({ reviews, timezone }: { reviews: CardReview[]; timezone: string }) {
  return <>{!reviews.length && <p className="resource-note">No reviews yet.</p>}<ol className="flashcard-history-list">{reviews.map((review) => <li key={review.id}><div className="flashcard-history-meta"><strong>{ratingLabel(review.rating)}</strong><time dateTime={review.reviewed_at}>{flashcardTimestamp(review.reviewed_at, timezone)}</time><span>{review.previous_interval_days} → {review.next_interval_days} days</span></div><p className="resource-note">Next review: {flashcardTimestamp(review.next_review_at, timezone)} · Algorithm {review.algorithm_version}</p><details><summary>Content at review</summary><p className="flashcard-text">{review.front_snapshot}</p><p className="flashcard-text">{review.back_snapshot}</p></details></li>)}</ol></>;
}
export function CardHistory({ card, close }: { card: Card; close: () => void }) {
  const [offset, setOffset] = useState(0);
  const history = useQuizLoad(useCallback(async (signal) => ({ ...(await getCardReviews(card.id, offset, signal)), offset }), [card.id, offset]));
  const { timezone, timezoneNote, timezoneFailed, retryTimezone } = useFlashcardTimezone();
  return <QuizDialog title="Flashcard review history" close={close}><p className="flashcard-text">{card.front}</p><div className="resource-timezone"><p className="resource-note">{timezoneNote}</p>{timezoneFailed && <button type="button" className="secondary-button" onClick={retryTimezone}>Retry timezone</button>}</div><LoadNotice loading={history.loading} error={history.error} retry={history.retry} />{history.data && <><CardHistoryView reviews={history.data.reviews} timezone={timezone} /><Pagination offset={history.data.offset} total={history.data.total} busy={history.loading} change={setOffset} /></>}</QuizDialog>;
}
