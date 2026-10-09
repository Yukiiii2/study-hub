# Phase 10 Assessments — Design and Implementation Plan

Use the existing private FastAPI domains, shared authenticated Next.js layout and
read-only-first workbook CLI patterns. Standing approval covers this additive
phase. No dependencies, AI, advanced analytics or destructive cleanup.

## Model and contract

Revision `0008_assessments` follows `0007_flashcards`.
`assessments`: id, required profile user_id, title(200), description nullable(5000),
scheduled_at nullable timestamptz, status planned/completed/cancelled/archived,
source_key nullable (unique per owner, CLI only), created_at/updated_at.
`assessment_topics`: assessment_id,user_id,topic_id,display_order; unique assessment/topic.
`assessment_subjects`: assessment_id,user_id,subject_id,display_order; only explicit
whole-subject coverage, not subject headers. Subject identity for selected topics
is derived. Do not store a selected topic redundantly under whole-subject coverage.
`assessment_attempts`: id,assessment_id,user_id,started_at/completed_at nullable,
score/max_score/percentage nullable, notes nullable(5000), created_at/updated_at.
Score pair must be both absent or both supplied, finite nonnegative score
(numeric18,4: at most 14 integer digits and four fractional digits),
positive max_score, score <= max_score and completed_at required when scored.
Percentage is backend-derived score/max_score*100, rounded to four decimal places.
If both timestamps are present, completed_at >= started_at. No fabricated result.
Completed results may be manually corrected through PATCH; history stays separate
from definitions. DELETE archives a definition and retains coverage/attempts.
All four tables owner SELECT RLS, no browser writes, composite owner FKs. API
ownership is always derived from verified identity; extra request fields forbidden.

## API / frontend DTO

Create/PATCH definition fields title,description,scheduled_at,status,topic_ids,
subject_ids (whole subjects only). At least one coverage ID is optional: a definition
can be authored before coverage is known. Each list max500, unique UUIDs, matching
active curriculum, no topic/whole-subject overlap. Partial PATCH merges/validates
the complete resulting coverage transactionally. Archived definitions remain
readable for history; new/edited attempts on archived definitions return409.
GET list accepts status(all default excludes archived unless status=archived),
q title search, limit50/max100, offset0; order scheduled_at NULLS LAST then created/id.
GET/POST `/api/assessments`, GET/PATCH/DELETE `/api/assessments/{id}`.
POST/GET `/api/assessments/{id}/attempts`; PATCH `/api/assessment-attempts/{id}`.
Create201, read/patch200, archive204; foreign/missing404, invalid422, archived409,
sanitized dependency503.

Assessment response: id,title,description,scheduled_at,status,created_at,updated_at,
topic_ids,subject_ids,coverage_topics:[{id,subject_id,code,title}],
coverage_subjects:[{id,code,name,scope:all_topics|selected_topics}],topic_count.
List `{assessments,total}`. Detail adds `readiness`:
`{topic_count,total_videos,completed_videos,video_completion_percentage,
quiz_graded_answers,quiz_correct_answers,quiz_accuracy_percentage,
active_flashcards,reviewed_flashcards,due_flashcards,overdue_flashcards,as_of,timezone}`.
Effective topics union exact topic coverage and topics in whole-subject scope.
Videos join these topics and the current user's progress. Quiz answers use only
completed own attempts and their immutable question-snapshot topic associations,
including unanswered (incorrect) covered questions and repeat attempts. Recall
uses own active cards with covered topic_id or subject_id in an explicit whole
subject, including cards without topic only for whole-subject coverage. Reviewed
means history exists, not mastered. Due <=server now, overdue <profile local-day start.
Percentages nullable when denominator is zero; never claim readiness or mastery.
No dedicated summary endpoint; detail carries components from one read snapshot.

Attempt inputs started_at,completed_at,score,max_score,notes; percentages/user IDs
not accepted. Response id,assessment_id,started_at,completed_at,score,max_score,
percentage,notes,created_at,updated_at (JSON numeric fields, nullable). List
`{attempts,total}` with limit50/max100, offset0, newest created/id first.

## Workbook

Inspect ASSESSMENTS row1 B/D/F/H/J/L/N subject headers. Five merged section
titles A2/A11/A22/A34/A46 are literal and preserved, including MONTLY spelling.
No dates exist. Literal subject-column coverage only; never formulas/booleans.
Exact subject+whitespace-normalized title match only. No fuzzy aliases. Explicit
AP 'All topics' in fifth section gives whole AP scope and supersedes individual
AP topic links in that section. Unknown labels are excluded and reported; partial
import descriptions state excluded counts, not complete coverage. No scores/history.
Stable source_key `project-1:ASSESSMENTS:A<row>`; compare title/description/null date/
planned status/exact coverage sets. Unchanged reruns propose zero inserts; edits,
source-key conflicts or unkeyed same-title candidates reject, never overwrite.
Require explicit existing owner before commit. Dry run and source mapping report
come before transactional insert-only commit; serialize by owner and re-plan
inside transaction. No user guessing or cross-owner records in reports.

## Work and focused verification

- Backend schemas/repository/services/routes and additive migration; tests first for
  percentages, partial validation, ownership, archival and readiness denominators.
- Frontend services, /assessments and /assessments/[id], coverage editor, manual
  results/history, readiness components, nav. Reuse native modal, selectors, dark
  compact rows; existing Auth provider unchanged. Dates use profile timezone.
- Workbook parser/import CLI and safe dry-run/migration/second-run reports; focused
  parser and conflict/idempotency tests. Real owner input required before writes.
- Apply migration; synthetic authenticated CRUD, invalid coverage/scores, isolation,
  readiness, RLS/grants checks; clean only temporary fixtures/accounts.
- Frontend focused render/state checks, build/TypeScript and route smoke. Relevant
  DATABASE/API/IMPORTS/README/ROADMAP updates; review/stage only Phase10 files.
- Commit `feat: add assessments`, push main, stop before Phase11.

Preserve the user's existing uncommitted frontend/next-env.d.ts edit. Never stage
environment files, workbook, credentials, fixtures/uploads or build output.

## Verified outcome

Migration `0008_assessments` applied. Eighteen focused backend/import tests pass,
as do the frontend state/render checks and production build with TypeScript.
Authenticated synthetic API checks cover definition/coverage CRUD, result creation
and correction, invalid inputs, owner isolation, real video/quiz/recall components,
immutable quiz coverage, RLS/grants and history-preserving archival. Temporary
accounts and their data were removed. HTTP smoke checks cover list/detail and
existing Flashcards/Recall routes; interactive browser automation was not performed.
Review caught and fixed precision/DST loss on unrelated date-field edits; unchanged
instants now retain their exact value, with regression checks.

Workbook dry run: five inserts, zero blocking errors. Transactional import created
five definitions, 71 topic links and one whole AP link for the explicitly selected
owner. Seventy-four labels remain excluded/reported, with partial-coverage notices.
Zero source dates/results/history imported. Second dry run: zero inserts, five
unchanged, zero errors. All imported detail/readiness reads were verified.
