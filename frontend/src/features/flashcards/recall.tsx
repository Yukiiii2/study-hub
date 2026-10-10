"use client";

import Link from "next/link";
import { PageHeader } from "@/components/page-header";
import { StatusBadge } from "@/components/study-ui";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { getCard, getDueCards, reviewCard, flashcardError, type Card, type CardReview, type DueSummary, type QueueMode, type Rating } from "@/services/flashcards";
import { useAuth } from "@/features/auth/auth-provider";
import { getSubjects } from "@/services/subjects";
import { LoadNotice, Pagination, QuizDialog, useQuizLoad } from "@/features/quizzes/shared";
import { DeckSelector } from "./deck-selector";
import { cardIsDue, confirmReview, flashcardTimestamp, pendingReview, ratingLabel, type PendingReview } from "./review-state";
import { clearReviewRecovery, readReviewRecovery, rememberReview, reviewStorage, type ReviewMetadata } from "./review-recovery";

export function RecallSummary({ summary, timezone, asOf }: { summary: DueSummary; timezone: string; asOf: string }) {
  return <div className="flashcard-recall-summary"><dl className="recall-queue-metrics"><div><dt>Overdue</dt><dd>{summary.overdue}</dd></div><div><dt>Due today</dt><dd>{summary.due_today}</dd></div><div><dt>Upcoming</dt><dd>{summary.upcoming}</dd></div></dl><p className="resource-note">Counts as of {flashcardTimestamp(asOf, timezone)}. Dates use {timezone}.</p></div>;
}
export function RecallCardView({ card, revealed, busy, pending, reveal, rate, timezone, allowReview }: { card: Card; revealed: boolean; busy: boolean; pending: PendingReview | null; reveal: () => void; rate: (rating: Rating) => void; timezone: string; allowReview: boolean }) {
  return <section className="flashcard-recall-card" aria-label="Current flashcard"><div className="recall-card-context"><StatusBadge tone="warning">{revealed ? "Answer revealed" : "Recall the answer"}</StatusBadge></div><h2 className="flashcard-text">{card.front}</h2><p className="resource-note">Due <time dateTime={card.next_review_at}>{flashcardTimestamp(card.next_review_at, timezone)}</time></p>{!revealed ? <button className="primary-button" disabled={busy} onClick={reveal}>Reveal answer</button> : <><div className="flashcard-recall-answer"><h3>Answer</h3><p className="flashcard-text">{card.back}</p>{card.notes && <p className="resource-note flashcard-text">{card.notes}</p>}</div>{allowReview ? <div className="flashcard-rating-actions" role="group" aria-label="Rate your recall">{pending ? <button className="primary-button" disabled={busy} onClick={() => rate(pending.body.rating)}>{busy ? "Saving review…" : `Retry ${ratingLabel(pending.body.rating)}`}</button> : (["again", "hard", "good", "easy"] as Rating[]).map((rating) => <button className="secondary-button" key={rating} data-rating={rating} disabled={busy} onClick={() => rate(rating)}>{ratingLabel(rating)}</button>)}</div> : <p className="resource-note">This card is not due yet. It cannot be rated early.</p>}</>}{card.resource_id && <p className="resource-note">Source: <Link className="quiz-text-link" href={`/library/${card.resource_id}`}>Open resource{card.source_page ? ` · Page ${card.source_page}` : ""}</Link></p>}</section>;
}
export function RecallPage() {
  const { user } = useAuth();
  return user ? <RecallWorkspace key={user.id} ownerId={user.id} /> : null;
}
function RecallWorkspace({ ownerId }: { ownerId: string }) {
  const router = useRouter();
  const [filters, setFilters] = useState({ mode: "due" as QueueMode, subject_id: "", deck_id: "", offset: 0 });
  const [revealed, setRevealed] = useState(false);
  const [pending, setPending] = useState<PendingReview | null>(null);
  const [busy, setBusy] = useState(false);
  const [writeError, setWriteError] = useState<string | null>(null);
  const [consumed, setConsumed] = useState<string[]>([]);
  const [lastReview, setLastReview] = useState<CardReview | null>(null);
  const [discard, setDiscard] = useState(false);
  const [recovered, setRecovered] = useState(false);
  const [recoveryUnavailable, setRecoveryUnavailable] = useState(false);
  const [recoveryChecked, setRecoveryChecked] = useState(false);
  const [recoveryMetadata, setRecoveryMetadata] = useState<ReviewMetadata | null>(null);
  const [recoveryError, setRecoveryError] = useState<string | null>(null);
  const [recoveryRetry, setRecoveryRetry] = useState(0);
  const [leave, setLeave] = useState<string | null>(null);
  const pendingRef = useRef<PendingReview | null>(null);
  const inFlight = useRef(false);
  const recoveryRef = useRef<ReviewMetadata | null>(null);
  const initialized = useRef<string | null>(null);
  const subjects = useQuizLoad(useCallback((signal) => getSubjects(signal), []));
  const queue = useQuizLoad(useCallback(async (signal) => ({ ...(await getDueCards({ ...filters, limit: 20 }, signal)), filters }), [filters]));
  const card = pending?.card ?? queue.data?.cards.find((item) => !consumed.includes(`${item.id}:${item.review_revision}`));
  const timezone = queue.data?.timezone ?? "Asia/Manila";
  const allowReview = !!pending || !!card && !!queue.data && cardIsDue(card, queue.data.as_of) && queue.data.filters.mode !== "upcoming";
  const changedRecoveredContent = !!pending && pending.card.review_revision !== pending.body.expected_revision;
  const locked = !!pending || !!recoveryMetadata || !recoveryChecked;
  useEffect(() => {
    if (!ownerId || initialized.current === ownerId && !recoveryRef.current) return;
    if (initialized.current !== ownerId) {
      initialized.current = ownerId;
      const stored = readReviewRecovery(reviewStorage(), ownerId);
      setRecoveryUnavailable(!stored.available); recoveryRef.current = stored.metadata; setRecoveryMetadata(stored.metadata);
      if (!stored.metadata) { setRecoveryChecked(true); return; }
    }
    const metadata = recoveryRef.current;
    if (!metadata) return;
    const controller = new AbortController(); setRecoveryError(null);
    void getCard(metadata.card_id, controller.signal).then((ownedCard) => {
      if (controller.signal.aborted) return;
      const restored = { card: ownedCard, body: { rating: metadata.rating, expected_revision: metadata.expected_revision, request_id: metadata.request_id } };
      pendingRef.current = restored; setPending(restored); setRevealed(true); setRecovered(true); setRecoveryMetadata(null); recoveryRef.current = null;
    }).catch((failure) => { if (!controller.signal.aborted) setRecoveryError(flashcardError(failure)); }).finally(() => { if (!controller.signal.aborted) setRecoveryChecked(true); });
    return () => controller.abort();
  }, [ownerId, recoveryRetry]);
  useEffect(() => { if (!pendingRef.current) setRevealed(false); }, [card?.id, card?.review_revision]);
  useEffect(() => {
    if (!recoveryUnavailable || !pending && !recoveryMetadata) return;
    const warn = (event: BeforeUnloadEvent) => { event.preventDefault(); event.returnValue = ""; };
    const guardLink = (event: MouseEvent) => {
      if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || !(event.target instanceof Element)) return;
      const link = event.target.closest<HTMLAnchorElement>("a[href]");
      if (!link || link.target === "_blank" || link.hasAttribute("download")) return;
      const destination = new URL(link.href);
      if (destination.origin !== window.location.origin || destination.pathname === window.location.pathname) return;
      event.preventDefault(); if (!inFlight.current) setLeave(`${destination.pathname}${destination.search}${destination.hash}`);
    };
    window.addEventListener("beforeunload", warn); document.addEventListener("click", guardLink, true);
    return () => { window.removeEventListener("beforeunload", warn); document.removeEventListener("click", guardLink, true); };
  }, [recoveryUnavailable, pending, recoveryMetadata]);
  function changeFilters(next: typeof filters) { if (pendingRef.current || recoveryRef.current || inFlight.current || !recoveryChecked) return; setRevealed(false); setWriteError(null); setFilters(next); }
  function refresh() { if (pendingRef.current || recoveryRef.current || inFlight.current || !recoveryChecked) return; setRevealed(false); setWriteError(null); queue.retry(); }
  async function rate(rating: Rating) {
    if (inFlight.current || !card || !recoveryChecked || !revealed || !allowReview) return;
    let request = pendingRef.current;
    if (!request) { request = pendingReview(card, rating); pendingRef.current = request; setPending(request); setRecoveryUnavailable(!rememberReview(reviewStorage(), ownerId, request)); }
    inFlight.current = true; setBusy(true); setWriteError(null);
    try { await confirmReview(request, reviewCard, (review) => { clearReviewRecovery(reviewStorage(), ownerId); setConsumed((current) => [...current, `${request!.card.id}:${request!.body.expected_revision}`]); setLastReview(review); pendingRef.current = null; setPending(null); setRecovered(false); setRevealed(false); queue.retry(); }); }
    catch (failure) { setWriteError(flashcardError(failure)); }
    finally { inFlight.current = false; setBusy(false); }
  }
  function discardAndRefresh() { if (inFlight.current) return; clearReviewRecovery(reviewStorage(), ownerId); pendingRef.current = null; recoveryRef.current = null; setRecoveryMetadata(null); setRecoveryError(null); setRecoveryChecked(true); setPending(null); setRecovered(false); setRevealed(false); setWriteError(null); setDiscard(false); queue.retry(); }
  return <><PageHeader title="Recall" description="Reveal one card, then rate what you remembered." actions={<Link className="secondary-button" href="/flashcards">Manage flashcards</Link>} /><div className="resource-filters"><label>Queue<select value={filters.mode} disabled={busy || locked} onChange={(event) => changeFilters({ ...filters, mode: event.target.value as QueueMode, offset: 0 })}><option value="due">Due now</option><option value="overdue">Overdue</option><option value="today">Due today</option><option value="upcoming">Upcoming</option></select></label><label>Subject<select value={filters.subject_id} disabled={busy || locked || !subjects.data} onChange={(event) => changeFilters({ ...filters, subject_id: event.target.value, offset: 0 })}><option value="">All subjects</option>{subjects.data?.map((subject) => <option key={subject.id} value={subject.id}>{subject.code}</option>)}</select></label><DeckSelector value={filters.deck_id} filter disabled={busy || locked} change={(deck_id) => changeFilters({ ...filters, deck_id, offset: 0 })} /><button className="secondary-button" disabled={busy || locked} onClick={refresh}>Refresh queue</button></div><LoadNotice loading={false} error={subjects.error} retry={subjects.retry} /><LoadNotice loading={queue.loading} error={queue.error} retry={refresh} />{queue.data && <RecallSummary summary={queue.data.summary} timezone={timezone} asOf={queue.data.as_of} />}{queue.data && queue.data.filters !== filters && <p className="resource-note">Showing the last loaded queue while filters refresh.</p>}{lastReview && <p className="planner-notice" role="status">{ratingLabel(lastReview.rating)} saved. Next review: {flashcardTimestamp(lastReview.next_review_at, timezone)}.</p>}{writeError && <div><p className="auth-error" role="alert">{writeError} The original card, revision and rating are kept for retry.</p><button className="secondary-button" disabled={busy} onClick={() => setDiscard(true)}>Discard pending review and refresh</button></div>}
    {recoveryMetadata && <div className="flashcard-recovery-panel"><p role="status">Loading an unconfirmed review from this browser session. No rating is submitted automatically.</p>{recoveryError && <><p className="auth-error" role="alert">{recoveryError}</p><button className="secondary-button" onClick={() => setRecoveryRetry((value) => value + 1)}>Retry recovery</button><button className="secondary-button" onClick={() => setDiscard(true)}>Discard pending review and refresh</button></>}</div>}
    {recovered && pending && <p className="planner-notice" role="status">Unconfirmed {ratingLabel(pending.body.rating)} review restored. Retry the original request to check whether it was already saved. No new rating is submitted automatically.</p>}
    {recoveryUnavailable && (pending || recoveryMetadata) && <p className="auth-error" role="alert">Browser review recovery is unavailable. Keep this page open until your rating is confirmed, or explicitly discard it before leaving.</p>}
    {changedRecoveredContent && pending ? <section className="flashcard-recovery-panel"><p>The card changed after the original review. Retry that original request before reviewing the current content.</p><button className="primary-button" disabled={busy} onClick={() => void rate(pending.body.rating)}>{busy ? "Checking review…" : `Retry ${ratingLabel(pending.body.rating)}`}</button><button className="secondary-button" disabled={busy} onClick={() => setDiscard(true)}>Discard pending review and refresh</button></section> : card && !recoveryMetadata && <RecallCardView card={card} revealed={revealed} busy={busy || queue.loading && !pending || !recoveryChecked} pending={pending} reveal={() => setRevealed(true)} rate={(rating) => void rate(rating)} timezone={timezone} allowReview={allowReview} />}{queue.data && !card && !queue.loading && !recoveryMetadata && <section className="resource-empty"><h2>This review view is complete</h2><p>No cards remain in this loaded view. Refresh to check the queue or choose another mode.</p><Link className="secondary-button" href="/flashcards">Open flashcards</Link></section>}{queue.data && <Pagination offset={queue.data.filters.offset} total={queue.data.total} busy={queue.loading || busy || locked} change={(offset) => changeFilters({ ...filters, offset })} />}
    {discard && <QuizDialog title="Discard pending review?" busy={busy} close={() => setDiscard(false)}><p>The rating has not been confirmed in this page. A previous request may already have been saved by the server. Refresh will load the current state without submitting another review.</p><div className="planner-dialog-actions"><button className="secondary-button" disabled={busy} onClick={() => setDiscard(false)}>Keep retrying</button><button className="primary-button" disabled={busy} onClick={discardAndRefresh}>Discard and refresh</button></div></QuizDialog>}
    {leave && <QuizDialog title="Leave unconfirmed review?" busy={busy} close={() => setLeave(null)}><p>Browser recovery is unavailable. Leaving can lose the request needed to safely retry this unconfirmed rating.</p><div className="planner-dialog-actions"><button className="secondary-button" onClick={() => setLeave(null)}>Stay here</button><button className="primary-button" onClick={() => { const destination = leave; discardAndRefresh(); setLeave(null); router.push(destination); }}>Discard and leave</button></div></QuizDialog>}
  </>;
}
