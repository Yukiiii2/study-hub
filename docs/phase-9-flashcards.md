# Phase 9 Flashcards and Recall — Design and Implementation Plan

Goal: private manually authored flashcards, due review and deterministic scheduling
using the existing FastAPI/PostgreSQL and shared authenticated Next.js architecture.
No new dependencies, credentials, source-history writes or later-phase features.

## Model and security

Add revision `0007_flashcards` after `0006_quizzes`: flashcard_decks, flashcards,
flashcard_reviews. Every table has mandatory profile ownership, composite owner
FKs, RLS and authenticated owner SELECT only; browser writes remain denied.
Backend always scopes queries by verified user. Active subject/topic relations and
own deck/resource/PDF page are validated. A subject-specific deck only accepts
matching-subject cards; changing its subject rejects conflicting assigned cards.

Deck: id, subject_id nullable, title(200), description nullable(2000), is_archived,
created_at/updated_at. Card: id, deck_id/subject_id/topic_id/resource_id/source_page
nullable, front(5000), back(12000), notes nullable(5000), status(active/suspended/
archived), interval_days(0..365), next_review_at, review_revision(nonnegative),
created_at/updated_at. Current state lives on the card, no extra state table.
New cards are active and due immediately using server time. Editing content keeps
the existing schedule but increments revision to invalidate stale revealed content.
Suspended/archived cards never appear in review queues.

DELETE card archives, retaining history. DELETE deck archives and detaches its own
cards transactionally, retaining content, schedules and history. No destructive
migration or existing-data cleanup. Resource deletion detaches current source/page
via a restricted trigger without destroying flashcard or review history.

Reviews: id, user_id, flashcard_id, request_id(UUID), previous_revision,
reviewed_at/server time, rating, previous_interval_days, next_interval_days,
next_review_at, algorithm_version, front_snapshot/back_snapshot, created_at.
Unique(user_id,request_id) and unique(flashcard_id,previous_revision) protect retries.
Archive/edit/review serialize on the same card. Review accepts rating plus
expected_revision and request_id; client cannot set owner, timestamps or interval.
Exact retry returns the same review; reused ID with different card/rating/revision
or stale revision returns 409. Future/nonactive cards cannot be reviewed early.

## Exact scheduling v1

Pure backend function uses aware UTC server time, not browser dates. Prior interval
is integer days; cap 365. Again resets interval to 0, due in 10 minutes.
Hard: max(1,ceil(previous*1.2)) days. Good: max(1,ceil(previous*2.5)) days.
Easy: max(4,ceil(previous*3.5)) days. First review therefore Hard=1, Good=1,
Easy=4. Multipliers use integer arithmetic to avoid floating-point rounding.
No ease factor, partial-day growth, external scheduler or claimed retention score.

## APIs and DTOs

All endpoints authenticated; UUID/body validation 422; foreign/missing 404;
stale/nonactive/not-due/conflicts 409; unavailable dependencies sanitized 503.
Create 201, read/patch/review 200, delete 204. Extra body fields forbidden.
Card/deck/review DTOs omit user_id and internal request identity except review
request_id for client retry correlation. Timestamps remain aware.

- GET/POST /api/flashcard-decks -> {decks,total}/Deck; GET/PATCH/DELETE
  /api/flashcard-decks/{id}. Patch accepts partial title/description/subject_id.
- GET/POST /api/flashcards -> {cards,total}/Card; GET/PATCH/DELETE
  /api/flashcards/{id}. Create accepts front/back, optional associations/notes/status;
  PATCH accepts partial editable fields only, never scheduling state.
- GET /api/flashcards/due -> {cards,total,summary:{overdue,due_today,upcoming},
  timezone,as_of}; mode=due(default)/overdue/today/upcoming, subject_id/deck_id
  filters, limit50/max100, offset0. Define overdue as due before profile local-day
  start, due_today from day start through now, upcoming strictly after now.
  Due mode includes overdue and due_today, earliest next_review_at/id first.
  This deliberately excludes cards later today until their actual due time.
- POST /api/flashcards/{id}/review -> Review; body
  {rating:again|hard|good|easy,expected_revision:int,request_id:UUID}.
- GET /api/flashcards/{id}/reviews -> {reviews,total}; newest first, limit/offset.
- Card list filters: subject_id/topic_id/deck_id/resource_id/status/q; active
  default, query status=all includes suspended/archived. Deck lists exclude archive.
- Deck list filters subject_id/q; all lists bounded and safely escaped search.

## Frontend

Preserve shell/fonts/colors/native modal pattern and authenticated API client.
/flashcards offers compact cards/decks, search/status/subject/deck filters, manual
editor, history, suspend/reactivate/archive and deck CRUD. Reuse subject/topic and
resource selectors. /recall shows actual due/overdue/upcoming counts and filters;
one front at a time, explicit reveal, then four ratings. UI never computes dates.
Await confirmed review, retain revealed card/request identity on failures, and
then advance; refresh loads more, never silently submits or auto-reviews.
An unconfirmed rating stores only owner-scoped card ID, request ID, rating and
revision in sessionStorage. Remount/reload retrieves the owned card through the
API and offers an explicit retry of the original request, never an automatic POST.
Content changes require resolving that retry before showing a new review. No card
text or credentials are stored for recovery; unavailable storage warns before leaving.
Profile timezone comes from queue or existing timezone helper, not browser zone.
Quiz completed incorrect-answer review opens the same editable card form with
prompt/option-text answer/explanation; no automatic persistence or generation.
No new auth provider/guard/listener. Add small real recall summary only if useful
without expanding the dashboard. Implemented as recall_summary:{overdue,due_today}
on the existing dashboard response with a compact section after Today/tasks.

## Tasks and verification

- [x] Backend: focused failing schema/scheduler/lifecycle tests, implement migration,
  schema/repository/services/routes; focused green checks and root integration.
- [x] Frontend: services, card/deck/editor/history/recall routes/nav/styles and manual
  quiz-mistake action; focused state/render tests and production build/TypeScript.
- [x] Workbook: read-only * Recall inspection with exact unique existing-topic
  matching, private history omitted; source report, zero card/review writes.
- [x] Integration: apply additive migration, two synthetic users, CRUD/association/
  ownership/due/review/grants/concurrent retry/quiz manual mapping checks; cleanup
  only created identities and synthetic resources. Route smoke checks.
- [x] Review relevant docs/diff, stage code/docs/safe report only, no environment,
  source workbook/uploads/temp fixtures/user next-env edit. One commit
  `feat: add flashcards and spaced repetition`, push main, stop before Phase 10.

Review focus: server-only dates; future-card denial; duplicate/stale submissions;
content edits after reveal; deck/resource owner isolation; immutable history after
editing/archiving; failed requests must not advance UI or lose a retry ID.

## Validation performed

Revision `0007_flashcards` applied successfully. The 29 focused backend checks pass.
Live authenticated checks pass for CRUD, association validation, due ordering and
dashboard counts, all four ratings and progression, identical and conflicting
concurrent submissions, immutable history, archive/source detachment, owner RLS
and denied browser writes. Temporary accounts, resources and their rows were cleaned up.
Frontend reveal/retry/recovery/empty-state and quiz integration checks pass; production
build includes TypeScript and both new routes. HTTP smoke checks pass for Flashcards,
Recall, Quizzes and Dashboard. Interactive browser automation was not performed.
Workbook analysis remains report-only, with zero card/review history imported.
