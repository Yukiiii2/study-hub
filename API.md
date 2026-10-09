# API.md

## Purpose

Initial REST contract direction between Next.js and FastAPI. Exact schemas are finalized feature-by-feature.

## Conventions

Base prefix: `/api`

Use conventional HTTP statuses. Do not leak secrets or raw internal stack traces.

## Foundation

Phases 1–6.5 implement `/health`, `/api/auth/me`, subject/topic reads, video reads/progress, owner-scoped planner APIs and a read-only dashboard summary documented below. Other routes remain future contract directions.

### GET /health

Response:

```json
{
  "status": "ok"
}
```

## Dashboard (implemented Phase 6.5)

### GET /api/dashboard

Requires the verified Supabase bearer identity; accepts no client ownership or date-range parameters. Missing/invalid authentication returns 401; provider/database/invalid stored-data failures return sanitized 503 responses. Reads a consistent, read-only PostgreSQL snapshot without creating plans or progress rows. Response:

- `date`, `timezone`, `generated_at`: today's date in the profile timezone and the aware response-generation instant.
- `today_events`: existing occurrence response fields plus nullable `subject_code` and `topic_title`. Includes all events overlapping the local day, ordered by start/id, using the same recurrence/snapshot/deletion rules as `/api/study-events`. Status is preserved, including completed/skipped/cancelled items.
- `upcoming_tasks`: existing task response fields plus nullable `subject_code` and `topic_title`. Only this user's pending tasks, at most five, ordered by `due_at ASC NULLS LAST`, then `created_at` and `id`. Overdue pending tasks remain visible.
- `subjects`: active subject response fields plus `topic_count`, `video_count` and `completed_video_count`, in existing curriculum order. Counts include all real topics/lectures, but completions belong only to the current user. Subjects with no topics/videos return real zero counts.
- `video_summary`: existing lecture-summary fields plus `remaining_videos` (total minus completed), aggregated across active subjects. Known durations only; no partial watch-time or composite progress calculation.
- `continue_video_subject_id`: first active subject in curriculum order with an in-progress lecture; otherwise the first with unfinished lectures; null when none remain. Clients may offer Browse Videos using a subject with lectures when all are complete.

No user IDs, tokens, source locators or private data from other users are returned. The frontend makes one summary request per Dashboard mount or explicit Refresh, uses the shared authenticated layout and keeps loaded content during refresh/failure. Existing APIs remain unchanged.

## Subjects

### GET /api/subjects

Requires `Authorization: Bearer <Supabase access token>`. Returns a JSON array of active subjects from PostgreSQL, ordered by `display_order`, then `code`, then `id`. Each item contains only `id`, `code`, `name`, `display_order`, and nullable `color_key`. Phase 3 removes the Phase 2 timestamps and active flag from the public response; the frontend uses the compact schema. No progress metrics are returned.

### GET /api/subjects/{subject_id}

Returns one active subject with the same fields as a list item. Missing or inactive subjects return 404.

### GET /api/subjects/{subject_id}/topics

Returns a **flat JSON array** of real topics for an active subject. Each item contains `id`, `subject_id`, nullable `parent_topic_id`, nullable `code`, `title`, nullable `description`, and `display_order`. Items are ordered by `display_order`, then `title`, then `id`. Siblings retain that order when the frontend reconstructs the hierarchy using `parent_topic_id`. No topics returns `[]`; a missing or inactive subject returns 404.

## Topics

### GET /api/topics/{topic_id}

Returns one topic with the same fields as the subject topic array. Missing topics or topics belonging to inactive subjects return 404.

All subject/topic GET routes independently require a verified Supabase bearer token. UUID path parameters are validated (422 for malformed UUIDs after authentication). Missing/invalid/expired sessions return 401. Authentication or database failures return sanitized 503 responses. No curriculum create/edit/delete routes are implemented.

The frontend walks topic records iteratively in parent-before-child order. Missing parents appear as roots; malformed cycles are visited at most once per topic so every record remains visible. Visual indentation is capped on deep trees to preserve mobile readability, while accessible text retains the actual level. No sample topics are seeded.

Topic/composite study progress remains undefined; only the documented video statuses are writable.

## Videos

All routes require a verified Supabase bearer token. Missing/inactive subject, topic, or video returns 404. Invalid paths/payloads return 422; authentication failures return 401; provider/database failures return sanitized 503. CORS permits GET, POST, PATCH and DELETE from explicit configured origins only; middleware handles preflight OPTIONS.

### GET /api/topics/{topic_id}/videos

Returns an ordered JSON array; an existing topic with no videos returns `[]`. Fields: `id`, `topic_id`, nullable `topic_code`, `topic_title`, `title`, nullable `duration_seconds`, `display_order`, the current user's `status`, nullable `watched_seconds`, and nullable `completed_at`. Missing progress logically returns `not_started` with null watched/completion values. No progress records are created by reads. Source import locators and user identities are not exposed.

### GET /api/subjects/{subject_id}/videos

Returns `{ "videos": [...], "summary": {...} }` for an active subject. Video fields match the topic endpoint. Ordering is topic display_order/id, then video display_order/id. Summary fields: `total_videos`, `completed_videos`, `total_duration_seconds`, `completed_duration_seconds`, `remaining_duration_seconds`, `unknown_duration_videos`. Known durations are summed; only completed video durations contribute to completed time. Remaining = known total minus completed. Unknown durations are counted and excluded from time totals. Existing subjects with no videos return an empty array and zero summary.

### PATCH /api/videos/{video_id}/progress

Request: `{ "status": "not_started" | "in_progress" | "completed" }`. Extra fields, including `user_id` and `watched_seconds`, are rejected. Returns the updated video with the same fields as GET. Ownership comes exclusively from the verified token. Progress is lazily inserted on start/completion; resetting an untouched video remains derived. Repeated completion preserves completed_at; moving to in_progress clears it; reset clears all timing/viewing values. No video player or viewing-time measurement is implemented. Frontend controls await successful persistence and refresh the subject response; failures do not show optimistic completion.

## Study planner (implemented Phase 6)

Every route independently verifies the bearer token. Ownership is derived from that identity; request bodies forbid extra fields, including `user_id`. Missing/other-user records return 404, invalid input/relationships/rules return 422, scheduling/active-session/series-shape conflicts return 409, and provider/database errors return sanitized 503. Create returns 201, successful patch/read 200, delete 204. Titles must be nonblank and at most 200 characters; notes at most 10,000. All timestamps supplied by clients must include an offset. Nullable fields can be explicitly cleared; required fields cannot be patched to null. Patches merge with the stored record before relationship/time validation.

| Method | Route | Behavior |
| --- | --- | --- |
| GET | `/api/study-plan/context` | `{timezone, active_session}` from the profile and own unfinished session |
| GET | `/api/study-events?start_at=...&end_at=...` | Overlapping one-offs/recurring occurrences, aware positive range up to 93 days; more than 2,000 results is rejected |
| POST | `/api/study-events` | Create one-off or weekly series |
| GET/PATCH/DELETE | `/api/study-events/{id}` | Read/edit/delete one event or explicitly selected series |
| PATCH/DELETE | `/api/study-events/{id}/occurrences/{YYYY-MM-DD}` | Independently edit/reschedule/status/delete one recurring occurrence |
| GET/POST | `/api/study-tasks` | List own tasks/newest first or create unscheduled work |
| PATCH/DELETE | `/api/study-tasks/{id}` | Edit/status/delete own task |
| POST | `/api/study-tasks/{id}/schedule` | Atomically create an event and schedule its pending task |
| GET | `/api/study-sessions` | Own sessions newest first, at most 100; optional aware start/end overlap filters |
| POST | `/api/study-sessions` | Start actual session using server time, optionally from an own event/occurrence |
| PATCH | `/api/study-sessions/{id}` | Stop actual session or edit its notes |

### Events and occurrences

Create fields: required `title`, `start_at`, `end_at`; optional nullable `subject_id`, `topic_id`, `recurrence_rule`, `notes`; `event_type` defaults general, `status` scheduled, `timezone` defaults to the configured profile timezone. Topic requires a valid active subject and must belong to it; start must precede end. Types: lecture/reading/drill/recall/quiz/assessment/general. Statuses: scheduled/completed/skipped/cancelled.

Event responses include `id`, subject/topic, title/type, start/end, timezone, status, recurrence_rule, notes, created/updated timestamps. List/occurrence-patch responses add `is_recurring`, nullable `occurrence_date` and `occurrence_id`. Recurring list `id` remains the series UUID; occurrence_date is its original local-date key even when moved. One-offs have null occurrence identity. No ownership UUID or secret is returned.

Rules use the documented weekly subset `FREQ=WEEKLY;BYDAY=MO,WE;UNTIL=20261231`. Selected days must be unique and include the anchor weekday. UNTIL is optional, inclusive in the series timezone, and cannot precede the anchor. Unsupported rules are rejected. Local wall-clock times are preserved. Invalid/ambiguous DST times require correction rather than a guessed offset.

Occurrence patches accept event-edit fields except timezone/recurrence_rule; they persist a snapshot. DELETE suppresses only that original date. Series patches retain snapshots and affect untouched occurrences; once snapshots exist, removing recurrence or changing timezone returns 409. Recurring template status stays scheduled; completion applies to occurrences. Series deletion preserves actual sessions and clears deleted references.

### Tasks

Fields: `id`, nullable subject/topic, title, task_type, nullable positive integer estimated_minutes, nullable aware due_at, status, nullable scheduled_event_id, created/updated timestamps. task_type uses the event types. Create/patch may set pending/completed/cancelled; scheduled is only set by the schedule endpoint. Schedule takes an EventCreate body retaining the task's subject/topic and scheduled status. It rejects duplicate scheduling and rolls back on failure. Deleting the linked event unlinks the task and returns scheduled status to pending. Explicitly patching pending unlinks a task while preserving its event; completing/cancelling a task does not complete/cancel the event.

### Sessions

Start body: nullable study_event_id, occurrence_date, subject_id, topic_id, notes. Event-linked sessions inherit curriculum context; supplied contradictory associations are rejected. A recurring event requires occurrence_date and stores an occurrence snapshot; a one-off forbids occurrence_date. No event permits independent actual activity. One active session per account is enforced; a second start returns 409.

Response fields: id, nullable study_event_id/occurrence_id/subject_id/topic_id, started_at, nullable ended_at/duration_seconds, notes, created_at. PATCH `{ "action": "stop" }` optionally accepts notes; notes-only patches are also accepted. Stop derives elapsed integer seconds from one server timestamp; repeated stops preserve the original end/duration. Clients cannot write timestamps/duration. Planned times are never overwritten.

## Resources

Implemented Phase 7; all six endpoints verify Supabase bearer identity. Missing
or other-user records return 404. Ownership/storage paths are never client inputs.
Invalid inputs return 422, unsupported type 415, size limit 413, and dependency
failures sanitized 503. No stack traces, credentials or storage locators are returned.

| Method | Route | Response/behavior |
| --- | --- | --- |
| GET | `/api/resources` | `{resources, total}`; optional subject_id/topic_id/resource_type/q filters; limit default50/max100, offset default0; newest first |
| POST | `/api/resources/upload` | Multipart file/title/subject_id/topic_id; 201 metadata after synchronous processing, including safely failed PDF extraction |
| GET | `/api/resources/{id}` | Own metadata |
| DELETE | `/api/resources/{id}` | 204 only after storage and metadata/sections deletion succeeds |
| GET | `/api/resources/{id}/download` | `{url, expires_in:120}`; download=true by default, false for browser open; transient signed link |
| GET | `/api/resources/{id}/content` | `{resource, sections, total_sections, headers, rows, row_count}`; PDF offset0/limit10/max20 pages; CSV first20 rows only |

Metadata includes id, nullable subject_id/topic_id/subject_code/topic_title, title,
original_filename, normalized mime_type, file_size_bytes, resource_type,
processing_status, nullable page_count/row_count/error_message, created_at/updated_at.
PDF sections include id, page_number, section_index and content. Download/open is
available for retained failed PDFs; no extracted content is invented.

Files are limited to 4 MiB, with a bounded multipart envelope, PDF/CSV only.
Topic requires a valid matching active subject. Extra ownership/path fields are
rejected. CSV uploads validate before persistence; arbitrary rows never enter
curriculum, quiz or flashcard tables. List/content reads are paginated/bounded.
Storage failure during deletion preserves database metadata and reports failure.
If database commit fails after object removal, retry deletion; no success is claimed.

## CSV import

- `POST /api/imports/csv/preview`
- `POST /api/imports/csv/commit`

Commit must validate again server-side.

## Quizzes

Implemented Phase 8. All routes authenticate the verified Supabase bearer user.
No client-controlled owner, score or correctness fields are accepted. Missing or
foreign records return 404; completed/mapping conflicts 409; invalid data 422;
dependency outages sanitized 503. Bank routes are author views; quiz detail and
active attempt DTOs omit keys/explanations/correctness, including nested options.

- GET/POST `/api/questions`: private bank list and creation; GET/PATCH
  `/api/questions/{id}`: author detail/edit/archive.
- GET/POST `/api/quizzes`: private list/builder creation; GET/PATCH
  `/api/quizzes/{id}`: detail, ordered builder editing/archive.
- POST `/api/quizzes/{id}/attempts`: start or resume the owner's active attempt.
- GET `/api/quiz-attempts`: paginated history, optional quiz_id filter.
- GET `/api/quiz-attempts/{id}`: persisted answers and frozen questions.
- POST `/api/quiz-attempts/{id}/answers`: `{question_id,selected_keys}`; validates
  question membership, keys and cardinality; saving does not reveal grading.
- POST `/api/quiz-attempts/{id}/complete`: atomic server grading; repeat returns
  the existing result without changing timestamps or scores.
- GET `/api/quiz-attempts/{id}/results`: completed review; 409 before completion.
- POST `/api/imports/questions/preview` and `/commit`: bounded CSV dry run and
  confirmed transactional insert; see IMPORTS.md.

List envelopes use questions/quizzes/attempts plus total, limit default50/max100
and offset0. Quiz definitions allow 1..100 unique active owned questions.
The exact DTO/request contracts and bounds are in [Phase 8](docs/phase-8-quizzes.md).
Personal self-study does not prevent an author reading their own Question Bank
keys; the taking flow never receives them until its attempt is completed.

## Flashcards

Implemented Phase 9; all requests authenticate verified Supabase identity. Missing
or foreign records return 404, stale/nonactive/not-due/conflicting actions 409,
validation 422 and dependency failures sanitized 503. Ownership, review dates and
intervals cannot be client inputs. Create returns 201, read/patch/review 200,
delete 204. Card/deck/review metadata never returns owner UUIDs.

| Method | Route | Behavior |
| --- | --- | --- |
| GET/POST | `/api/flashcard-decks` | Private deck list/create |
| GET/PATCH/DELETE | `/api/flashcard-decks/{id}` | Read/edit/archive; archival detaches cards, preserving schedules/history |
| GET/POST | `/api/flashcards` | Private filtered card list/create |
| GET/PATCH/DELETE | `/api/flashcards/{id}` | Read/edit/archive without deleting review history |
| GET | `/api/flashcards/due` | Active due/overdue/today/upcoming queue and real counts; optional subject/deck |
| POST | `/api/flashcards/{id}/review` | Atomic server scheduling and immutable review |
| GET | `/api/flashcards/{id}/reviews` | Paginated private history, newest first |

Lists use `{cards|decks|reviews,total}`, default limit50/max100 and offset0.
Card filters: subject_id/topic_id/resource_id/deck_id/status/q; default active,
status=all includes suspended/archived. Deck filters: subject_id/q; archive excluded.
Card front/back are required, with optional deck/subject/topic/resource/source_page,
notes and status; patches are partial, while required text/status cannot be null.
Subject-specific deck and topic/subject associations must match; sources must be own.

Review body: `{rating:again|hard|good|easy,expected_revision:int,request_id:UUID}`.
Returns one Review with server timestamps, prior/next interval, next_review_at,
algorithm_version and reviewed front/back snapshots. Exact retry returns that same
review; mismatched ID reuse or stale revision rejects without another history row.
Future cards cannot be reviewed early. Dates/intervals are backend-owned.

Queue response adds summary `{overdue,due_today,upcoming}`, timezone and as_of.
mode=due(default)/overdue/today/upcoming; earliest next_review_at/id first. Overdue
is before the profile local-day start; due_today runs from day start through now;
upcoming is strictly later than now, including cards later today. No read-time writes.
Dashboard now adds `recall_summary:{overdue,due_today}` using the same profile-day
and server as_of; no analytics endpoint is added. Exact bounds/fields are in
[Phase 9](docs/phase-9-flashcards.md).

## Assessments

Implemented Phase 10, authenticated and owner-scoped:

- `GET /api/assessments`: bounded list, status/q filters, limit50/max100, offset0.
- `POST /api/assessments`: title, optional description/scheduled_at/status,
  topic_ids and subject_ids (explicit whole-subject coverage).
- `GET /api/assessments/{id}`: coverage and transparent readiness components.
- `PATCH /api/assessments/{id}`: partial definition/coverage update.
- `DELETE /api/assessments/{id}`: archive; coverage and attempt history retained.
- `GET /api/assessments/{id}/attempts`: bounded persisted result history.
- `POST /api/assessments/{id}/attempts`: optional manual start/completion, score,
  max_score and notes. Null result is allowed; no fabricated score.
- `PATCH /api/assessment-attempts/{id}`: partial manual result correction.

Ownership and percentage are never client inputs. Score/max_score must be supplied
together, with positive maximum, 0 <= score <= maximum, and completed_at for scored
results. Scores allow up to 14 integer digits and four decimal places.
Percentage = score/max_score*100, server-rounded to four decimal places.
Both timestamps require completion >= start. Archived definitions reject attempt
writes; history remains readable. Foreign/missing404, invalid422, archived409,
dependency503 with safe errors. Create201, reads/patch200, archive204.

Selected-topic subject labels are derived; subject_ids means whole subjects only.
Reject overlap and invalid/inactive curriculum. Detail readiness uses effective
topic union, own video completions, graded own completed quiz snapshots, and own
active recall state. Zero-denominator percentages are null. No weighted readiness
score or mastery claim. Exact DTOs and filters: [Phase 10](docs/phase-10-assessments.md).

## Analytics

- `GET /api/analytics/overview`
- `GET /api/analytics/study-time`
- `GET /api/analytics/subjects/{subject_id}`

Analytics should derive from canonical source data.

## AI endpoints

Do not implement in foundation.

Later candidates:

- `POST /api/ai/resources/{resource_id}/summarize`
- `POST /api/ai/resources/{resource_id}/generate-quiz`
- `POST /api/ai/resources/{resource_id}/generate-flashcards`
- `POST /api/ai/resources/{resource_id}/ask`

AI endpoints must be authenticated, rate-aware, and source-grounded.

## Authentication

### Implemented GET /api/auth/me

Requires the Supabase session's access token in the Authorization bearer header. FastAPI forwards the token to Supabase Auth `/auth/v1/user` for verification rather than trusting decoded claims. Successful response:

```json
{"id": "verified-user-uuid", "email": "user@example.com"}
```

`email` may be null. No token, session, password, role key, or raw provider data is returned. Missing/invalid/expired tokens return 401 with `WWW-Authenticate: Bearer`; missing backend Auth configuration or provider failures return 503. `/health` remains public. There is no backend sign-in endpoint: the browser signs in directly through the official Supabase Auth client.

Frontend sends the authenticated user's bearer token for protected endpoints.

FastAPI validates identity and scopes user-owned data to that identity.

Do not trust `user_id` supplied in request bodies for ownership.
