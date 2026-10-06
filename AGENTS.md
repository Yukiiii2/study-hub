# AGENTS.md

## Purpose

Work efficiently, stay within the user's requested scope, and make the smallest correct change.

CPA Study Hub deliberately keeps the frontend and backend as separate applications inside one repository. Preserve that separation.

## Core rules

Before changing anything:

1. Identify the exact requested outcome.
2. Identify the authorized area: `frontend/`, `backend/`, database/migrations, documentation, or infrastructure.
3. Read only the minimum project context needed.
4. Make the smallest correct change.
5. Do not expand scope unless the requested work cannot be completed correctly without it.

If a material product or business decision is missing, ask rather than inventing behavior.

## Required context

Before user-facing frontend work, read:

- `PRODUCT.md`
- `DESIGN.md`
- `DESIGN_GUIDELINES.md`

Before backend/API/database/import/AI/deployment work, read the relevant files:

- `ARCHITECTURE.md`
- `DATABASE.md`
- `API.md`
- `IMPORTS.md`
- `AI.md`
- `DATA_AND_TELEMETRY.md`
- `DEPLOYMENT.md`
- `GIT_WORKFLOW.md`

Treat these Markdown files as project contracts.

## Repository boundaries

### `frontend/`

Responsible for:

- Next.js routes/pages
- React UI
- accessibility
- forms and browser interaction
- client state
- calling FastAPI
- documented browser-side Supabase Auth usage
- charts/presentation

Frontend must not own:

- privileged database access
- Supabase service-role credentials
- AI provider secrets
- PDF/CSV parsing
- quiz scoring rules
- spaced-repetition rules
- core progress calculations

### `backend/`

Responsible for:

- FastAPI routes
- validation
- business logic
- database access
- PDF/CSV processing
- quiz logic
- flashcard/recall scheduling
- analytics calculations
- AI integrations
- privileged Supabase operations

Do not bypass FastAPI by moving business logic into Next.js for convenience.

## Strict scope

If the user specifies a file or area:

- edit only that scope
- inspect direct dependencies only when needed
- do not modify unrelated files
- ask before broadening the edit scope unless the broader phase prompt already authorizes it

Do not fix unrelated bugs, warnings, refactors, or visual inconsistencies unless they block the requested work.

## Frontend workflow

Before visible UI changes:

1. Read `PRODUCT.md`, `DESIGN.md`, and `DESIGN_GUIDELINES.md`.
2. Inspect the current implementation first.
3. Preserve existing behavior and visual language.
4. Treat supplied screenshots as primary references when provided.

Avoid:

- excessive rounded cards
- decorative gradients
- heavy shadows
- generic admin-dashboard visuals
- unnecessary motion
- unrelated redesigns

## Existing code

After implementation exists:

- inspect current code before modifying it
- reuse existing components/utilities
- preserve naming and file conventions
- follow established TypeScript and Python styles
- avoid unrelated refactors
- do not recreate working abstractions

## Database/API rules

- Check `DATABASE.md` before adding/changing tables.
- Check `API.md` before adding/changing endpoints.
- Use migrations for schema changes.
- Do not silently change API contracts.
- Never expose Supabase service-role credentials to the frontend.
- Never perform destructive migrations without explicit approval.
- Normalize spreadsheet/import data instead of mirroring tabs into database tables.

## Import rules

Google Sheets/XLSX, CSV, and PDF are input sources, not the production database.

- normalize before persistence
- validate before insertion
- report invalid rows/pages
- preserve source metadata where useful
- follow `IMPORTS.md`

## AI rules

Follow `AI.md`.

AI may assist with summaries, quizzes, flashcards, explanations, and source-grounded Q&A.

AI must not independently control progress history, deterministic quiz scores, schedule edits, recall history, assessment results, permissions, or account/security state.

Never expose AI keys to the frontend.

## Dependencies

Do not add/remove/upgrade dependencies unless the current phase requires them or the requested feature cannot reasonably be implemented without them.

Do not install future-phase dependencies early.

## Testing and commands

Do not run broad tests, builds, linting, type checks, browser automation, Docker, deployment, or repository-wide diagnostics by default.

Run only validation explicitly authorized by the current prompt.

Repository-initialization prompts may authorize dependency installation and narrow startup/syntax checks.

## Git

Follow `GIT_WORKFLOW.md`.

Never:

- force push
- rewrite remote history
- reset away user work
- commit secrets
- commit `.env` files
- commit unrelated changes

When a phase authorizes commit/push:

1. inspect the diff
2. stage only phase files
3. create a focused commit
4. push the current branch only if a remote is already configured and authentication succeeds
5. otherwise report the blocker and stop

## Deployment

Follow `DEPLOYMENT.md`.

Never invent credentials or project IDs.

A phase may explicitly authorize deployment. If external setup is missing, prepare deployable code and report the exact user action required.

## Completion

Report concisely:

- what changed
- files/areas changed
- important implementation decisions
- validation actually performed
- commit/push/deploy result if authorized
- blockers

Then stop.

## Main principle

Be intelligent in reasoning, conservative in scope, and economical in execution.

Read as much as needed. Change as little as needed. Run as little as needed. Do not guess important product behavior.
