# API.md

## Purpose

Initial REST contract direction between Next.js and FastAPI. Exact schemas are finalized feature-by-feature.

## Conventions

Base prefix: `/api`

Use conventional HTTP statuses. Do not leak secrets or raw internal stack traces.

## Foundation

Phases 1–6 implement `/health`, `/api/auth/me`, subject/topic reads, video reads/progress and owner-scoped planner APIs documented below. Other routes remain future contract directions.

### GET /health

Response:

```json
{
  "status": "ok"
}
```

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

- `GET /api/resources`
- `POST /api/resources/upload`
- `GET /api/resources/{resource_id}`
- `DELETE /api/resources/{resource_id}`
- optional later: `POST /api/resources/{resource_id}/process`

## CSV import

- `POST /api/imports/csv/preview`
- `POST /api/imports/csv/commit`

Commit must validate again server-side.

## Quizzes

- `GET /api/quizzes`
- `POST /api/quizzes`
- `GET /api/quizzes/{quiz_id}`
- `POST /api/quizzes/{quiz_id}/attempts`
- `POST /api/quiz-attempts/{attempt_id}/answers`
- `POST /api/quiz-attempts/{attempt_id}/complete`
- `GET /api/quiz-attempts/{attempt_id}/results`

## Flashcards

- `GET /api/flashcard-decks`
- `POST /api/flashcard-decks`
- `GET /api/flashcard-decks/{deck_id}/cards`
- `POST /api/flashcards`
- `PATCH /api/flashcards/{card_id}`
- `DELETE /api/flashcards/{card_id}`
- `GET /api/flashcards/due`
- `POST /api/flashcards/{card_id}/review`

Candidate review payload:

```json
{
  "rating": "good"
}
```

Backend owns next-review calculation.

## Assessments

- `GET /api/assessments`
- `POST /api/assessments`
- `PATCH /api/assessments/{assessment_id}`
- `DELETE /api/assessments/{assessment_id}`

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
