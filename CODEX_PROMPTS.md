# CODEX_PROMPTS.md

## How to use

For every Codex phase:

1. Attach/read all current project Markdown specification files.
2. Give Codex only the prompt for the current phase.
3. Review the result before starting the next phase.
4. Do not combine future phases just to save time.
5. Commit/push only when the phase prompt explicitly authorizes it.

## Prompt 01 — Repository foundation

Use `CODEX_KICKOFF_PROMPT.md`.

## Prompt 02 — Database + auth foundation

Planned scope:

- read all project docs
- configure Supabase contract
- migrations for profiles/subjects/topics
- seed CPA subjects
- backend auth validation
- minimal frontend auth wiring only if explicitly included
- no full subject UI yet

Write the exact prompt after reviewing Prompt 01 output.

## Prompt 03 — Subject system

- subject/topic API
- subject list/detail frontend
- follow design docs
- no spreadsheet migration

## Prompt 04 — Video tracking

- video schema/API
- user progress
- subject video UI
- progress summaries

## Prompt 05 — Spreadsheet migration

- inspect actual workbook export
- explicit mappings
- dry run/report first
- no ambiguous silent imports

## Prompt 06 — Calendar

- study events/tasks/sessions
- calendar views
- create/edit/delete/reschedule
- recurring schedule
- planned vs actual

## Prompt 07 — Resource library

- storage
- resources
- upload/list/filter
- processing states

## Prompt 08 — PDF/CSV processing

- text PDF extraction
- CSV preview/validation
- import templates

## Prompt 09 — Quiz engine

- question bank
- attempts
- scoring
- results

## Prompt 10 — Flashcards/recall

- decks/cards/reviews
- decide algorithm before implementation

## Prompt 11 — Assessments

## Prompt 12 — Analytics

## Prompt 13 — AI

## Prompt 14 — Polish

## Prompt 15 — Deployment
