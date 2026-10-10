# AI.md

## Purpose

Defines boundaries for AI-assisted features in CPA Study Hub.

AI is study assistance, not the authority for core application state.

## Provider architecture

Use a small backend provider abstraction.

Phase 12 provider:
- Gemini, with explicit backend-only `GEMINI_API_KEY` and `GEMINI_MODEL`.
- REST through existing HTTPX; no automatic provider/model fallback or AI SDK.

Future provider:
- OpenAI or another supported provider

Avoid coupling product logic tightly to one provider response format.

## Allowed capabilities

- summarize supported resources
- generate quiz questions
- generate flashcards
- explain quiz answers
- answer questions grounded in uploaded resources
- generate recall prompts
- assist with topic explanations

## AI must not own

AI must not independently determine or modify:

- deterministic quiz scores
- video completion
- study-event completion
- study-session duration
- permissions/authentication
- assessment results
- progress history
- destructive resource changes
- calendar changes without explicit user action

## Source grounding

For document-derived generation:

- use relevant document text where practical
- retain resource references
- retain page/section references where supported
- distinguish generated explanation from extracted source text

If the source does not support an answer, say so instead of fabricating a source-backed answer.

## Quiz generation

Store AI-generated questions with origin/source metadata.

For serious assessment use:

- validate structure
- keep source reference
- allow review/edit where appropriate
- do not imply exam-board endorsement

## Flashcard generation

Generated cards should:

- be concise
- focus on one concept
- preserve source reference
- avoid obvious duplicates

## Secrets

AI keys:

- backend only
- environment variables
- never committed
- never exposed in frontend bundles

## Cost/rate control

Phase 12 implements:

- rate limits
- request-size limits
- token/document limits
- clear processing/error states

Limits: prompt 2000 characters, request body 32 KiB, six PDF passages at 1800
characters each, total context 12000 characters, output 4096 tokens/24000 text
characters, provider envelope 96 KiB and total deadline 30 seconds. Draft counts
are 1..5 questions or 1..10 cards. Per process: one in-flight request per user,
five/minute, 100/day and eight calls concurrently. Counters reset on restart and
are not distributed; provider/project quotas remain the external hard cost limit.

## Implemented Phase 12 workflow

`/assistant` supports curriculum questions, PDF Q&A/summaries and editable quiz/
flashcard drafts. Quiz review explanations read owned completed snapshots, never
client-supplied keys, and cannot change grading. Generation never persists data.
Explicit confirmation reuses existing question/card APIs; AI cards save suspended
and enter Recall only after separate activation. Signed provenance describes
draft origin, not certification of later user edits. No raw prompts/chat history
are persisted or logged.

Retrieve selected owned ready PDF sections, not entire files. Specific searches
without relevant passages return insufficient context. Generic summaries use a
bounded selection, without claiming full-document coverage. Citations must quote
selected passages exactly and retain resource title/page references. Topic-only
help is identified as AI knowledge with curriculum context. Evidence pointers
do not guarantee the factual accuracy of every generated claim.

Document/user text is untrusted data, separate from fixed system instructions.
No tools/function calls, autonomous writes or client-controlled hidden prompts
are available. Provider failures are sanitized; credentials stay server-side.
See [Phase 12](docs/phase-12-ai-study.md),
[Gemini REST](https://ai.google.dev/api/generate-content),
[structured outputs](https://ai.google.dev/gemini-api/docs/structured-output) and
[model catalog](https://ai.google.dev/gemini-api/docs/models).

## Long-running processing

Start simply. If large document generation exceeds Vercel runtime constraints, introduce a worker/job system as a separate architecture decision.

## Accuracy

CPA review content can be high-stakes educational material.

Prefer source-grounded explanations and make source verification easy.

Do not silently change imported user-authored study material.
