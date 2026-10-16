"use client";

import Link from "next/link";
import { LoadingNotice } from "@/components/study-ui";
import { AIResponseView } from "./response-view";
import type { AssistantController } from "./use-assistant-controller";

export function AssistantConversation({ controller, compact = false, prompts = [] }: { controller: AssistantController; compact?: boolean; prompts?: string[] }) {
  const { turns, busy, error, pendingPrompt, pendingLabel, preview } = controller;
  return <div className="assistant-conversation" aria-label="Assistant conversation" aria-busy={busy}>
    {!turns.length && !busy && <section className="assistant-introduction"><h2>What are you studying?</h2><p>Ask about a concept, or choose a ready PDF for answers with source references.</p><p className="resource-note">Each question uses only your selected study sources. Page data and earlier messages are not sent automatically.</p>
      {!!prompts.length && <div className="assistant-starters">{prompts.map(prompt => <button type="button" className="secondary-button" key={prompt} onClick={() => controller.setPrompt(prompt)}>{prompt}</button>)}</div>}
    </section>}
    {turns.map(turn => <article className="assistant-turn" key={turn.id}><div className="assistant-user-message"><span>You</span><p>{turn.prompt}</p></div>
      <AIResponseView response={turn.response} />
      {("questions" in turn.response || "cards" in turn.response) && !turn.response.insufficient_context && <p className="assistant-draft-hint">{"questions" in turn.response ? turn.response.questions.length + " question drafts" : turn.response.cards.length + " flashcard drafts"}. Nothing is saved automatically.{compact && preview === turn.response && <> <Link className="quiz-text-link" href="/assistant">Expand to review, edit and confirm each save</Link>.</>}</p>}
    </article>)}
    {busy && <><div className="assistant-user-message"><span>You</span><p>{pendingPrompt}</p></div><LoadingNotice>{pendingLabel}</LoadingNotice></>}
    {error && <div className="assistant-inline-error"><p className="auth-error" role="alert">{error}</p><button type="button" className="secondary-button" disabled={busy} onClick={() => void controller.generate()}>Retry request</button><p className="resource-note">Your request is still in the composer.</p></div>}
    {/* Announce completion once, without rereading the entire transcript on every update. */}
    <span className="sr-only" role="status" aria-live="polite">{!busy && turns.length ? `Response ${turns.length} ready. Review the answer and its sources.` : ""}</span>
  </div>;
}
