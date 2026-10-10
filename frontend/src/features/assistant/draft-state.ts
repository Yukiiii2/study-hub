import type { AIResult, AICards, AIQuestions } from "@/services/ai";

export function hasDrafts(result: AIResult): result is AIQuestions | AICards {
  return !result.insufficient_context && ("questions" in result ? result.questions.length > 0 : "cards" in result && result.cards.length > 0);
}

// A failed/insufficient generation must not silently remove reviewed drafts.
export function retainDraftPreview(previous: AIQuestions | AICards | null, result: AIResult) {
  return hasDrafts(result) ? result : previous;
}

export class AIRequestGate {
  private revision = 0;
  private pending = false;
  begin(): number | null { if (this.pending) return null; this.pending = true; return ++this.revision; }
  current(ticket: number) { return this.pending && ticket === this.revision; }
  finish(ticket: number) { if (ticket === this.revision) this.pending = false; }
  invalidate() { this.revision++; this.pending = false; }
}

export function validContextId(value?: string) {
  return value && /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(value) ? value : "";
}
