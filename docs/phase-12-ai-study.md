# Phase 12 — AI study assistance

## Scope and architecture

FastAPI owns Gemini calls, source selection, response validation and cost bounds.
Use existing HTTPX (no AI SDK, vectors, workers or new chat/history tables).
Generation is transient. Existing authenticated Question Bank and flashcard create
APIs are the only save paths, after editable preview and explicit confirmation.
AI cards save suspended, outside Recall, until the user activates them separately.
Existing quiz grades, reviews, progress, schedules and security remain untouched.

Provider settings: backend-only GEMINI_API_KEY and GEMINI_MODEL (explicit model
identifier, no guessed credentials or automatic fallback). Use Gemini REST JSON
structured output, separate systemInstruction and study-material contents, no
tools/function calling, redirects or automatic retries. Missing provider returns
a sanitized 503. Deployment must configure provider quota/billing controls; no
external resource is created by this phase.

## API and DTO contract

Four authenticated POST routes under `/api/ai`:

- `/ask`: `{subject_id?,topic_id?,resource_id?,prompt}`.
- `/generate-quiz`: context fields plus `prompt?`, `count` (1..5, default3),
  `difficulty` (basic/intermediate/advanced, default intermediate).
- `/generate-flashcards`: same context plus optional attempt_id/question_id pair,
  optional prompt, count (1..10, default5).
- `/explain-answer`: `{attempt_id,question_id}` only. Read the owned submitted
  attempt snapshot; reject unfinished attempts. Never accept client answer keys,
  grades or hidden/system prompts. Quiz-mistake card generation uses the same
  trusted snapshot path. Retain a still-owned matching ready PDF association
  and its title when available; no source citations are implied without passages.
  Deleted or inaccessible sources do not prevent snapshot explanation.

All contexts require a valid subject/topic, a ready owned text PDF, or a completed
attempt/question pair. Topic must match subject; resource must match supplied
subject/topic when its own association is present. Resource-only context can
inherit its valid curriculum associations. No-context request gets a local
insufficient-context response without a model call. CSV/scanned/failed PDF text
is not invented. Missing/foreign resources and attempts return 404.

Common response metadata: `{provider,model,generated_at}` plus resolved `context`
`{subject_id,topic_id,resource_id}` and `grounding` (`resource`, `topic_context`,
`quiz_snapshot`, or `none`). Responses include `insufficient_context`, `notice`
(nullable), `citations` and `answer` for ask/explain, or `questions`/`cards` for
generation. Citation shape: `{resource_id,resource_title,page_number,quote}`.
Ask/explain never persist anything. Topic-only explanations are explicitly AI
knowledge with curriculum context, without invented document support.

Question draft shape: existing QuestionInput fields for single_select/true_false
only, plus `ai_draft_receipt`. Card draft: existing CardCreate fields, status
suspended and `ai_draft_receipt`. Generated structures reuse existing validators;
no invalid keys/options, duplicate prompts/cards or fabricated page references.
No draft contains a quiz ID, score, owner, scheduling field or provider secret.

## Source retrieval and validation

Select deterministic relevant passages from owned `document_sections`: bounded
query terms, at most six chunks/pages, at most 1800 characters per passage and
12000 source/context characters. Rank matches rather than downloading whole PDFs.
Summary/generation requests may use the first bounded passages where no specific
search is requested; unmatched specific Q&A returns insufficient context locally.
Include page metadata and mark all document text untrusted study material, not
instructions. Resource-based responses need model-selected chunk IDs and short
exact supporting quotes, verified against supplied passages. Return only valid
server-resolved citations. Invalid citations/output fail safely; source quotes
are evidence pointers, not a guarantee of model factual accuracy.

## Safety and bounds

Prompt <=2000 characters; AI request body <=32 KiB; resource context <=12000
characters; output <=4096 tokens and <=24000 text characters; provider response
<=96 KiB; total provider timeout30 seconds; no retries. Counts have server caps.
One generation in flight per user, at most five/minute and 100/day per user,
eight concurrent provider calls per process. Bound limiter memory; it stores
only user IDs/timestamps/counts, never prompts or documents. In-process limits
reset on restart and are not distributed; provider/project quota is the external
hard cost boundary. No raw provider exception/payload, prompt, file or token logs.

## Confirmed-save provenance

Add nullable ai_provenance JSONB to questions/flashcards and allow question origin
ai; keep existing RLS/grants. The provider service issues 24-hour HMAC draft
receipts binding owner, draft kind and bounded original provenance (provider,
model, generation time and resolved source IDs/pages). Derive a dedicated signing
key with a purpose-separated HMAC from the existing backend Supabase secret;
never expose that secret or require another environment key. No content or raw
prompt is stored in the receipt. Verification allows user edits before save, so
provenance describes draft origin, not a certification of subsequently edited
content. Client cannot assign provenance directly. Old source deletion need not
erase provenance; ownership is checked during retrieval and current save links
are validated by existing APIs. Normal manual/CSV behavior stays unchanged.

## Frontend and validation

Add compact `/assistant` within the shared authenticated layout: context selection,
ask/quiz/cards modes, source quotes, explicit editable save actions and recovery
states. Add secondary resource/topic shortcuts and completed quiz review explain/
card-draft actions. Preserve design tokens, stable session UX and primary tools.
Focused validation covers mocked-provider contracts/limits/injection separation,
auth/ownership/source selection, no automatic persistence, draft/save provenance,
suspended AI cards, quiz snapshot protection, frontend build/types and routes.
Live fixtures use temporary synthetic users/PDF sections and are cleaned up.
Missing Gemini configuration blocks live model verification, not code completion.
Review/stage Phase12 files only; preserve pre-existing next-env.d.ts edit. Commit
`feat: add AI study assistant`, push main, and stop before deployment/polish.

## Verification result

90 focused backend checks and the AI frontend interaction/render checks passed.
The production frontend build, including TypeScript, passed. Local health,
explicit CORS preflight and assistant routes passed; all four AI routes reject
unauthenticated requests. Real Supabase Auth/PostgreSQL verification with a
synthetic provider passed source isolation/citations, missing context, transient
drafts, explicit saves, unchanged quiz grading, limits and direct RLS isolation.
Temporary accounts and their records were removed and cleanup verified.
Live Gemini responses remain unverified until backend GEMINI_API_KEY and
GEMINI_MODEL are configured; no paid provider call or deployment was performed.
