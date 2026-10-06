# AI.md

## Purpose

Defines boundaries for AI-assisted features in CPA Study Hub.

AI is study assistance, not the authority for core application state.

## Provider architecture

Use a small backend provider abstraction.

Initial candidate:
- Gemini

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

Before production rollout add:

- rate limits
- request-size limits
- token/document limits
- clear processing/error states

## Long-running processing

Start simply. If large document generation exceeds Vercel runtime constraints, introduce a worker/job system as a separate architecture decision.

## Accuracy

CPA review content can be high-stakes educational material.

Prefer source-grounded explanations and make source verification easy.

Do not silently change imported user-authored study material.
