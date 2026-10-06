# API.md

## Purpose

Initial REST contract direction between Next.js and FastAPI. Exact schemas are finalized feature-by-feature.

## Conventions

Base prefix: `/api`

Use conventional HTTP statuses. Do not leak secrets or raw internal stack traces.

## Foundation

Phases 1–5 implement `/health`, `/api/auth/me`, subject/topic reads, video reads, and video progress updates documented below. Other routes remain future contract directions.

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

All routes require a verified Supabase bearer token. Missing/inactive subject, topic, or video returns 404. Invalid paths/payloads return 422; authentication failures return 401; provider/database failures return sanitized 503. CORS permits GET and PATCH from configured origins only.

### GET /api/topics/{topic_id}/videos

Returns an ordered JSON array; an existing topic with no videos returns `[]`. Fields: `id`, `topic_id`, nullable `topic_code`, `topic_title`, `title`, nullable `duration_seconds`, `display_order`, the current user's `status`, nullable `watched_seconds`, and nullable `completed_at`. Missing progress logically returns `not_started` with null watched/completion values. No progress records are created by reads. Source import locators and user identities are not exposed.

### GET /api/subjects/{subject_id}/videos

Returns `{ "videos": [...], "summary": {...} }` for an active subject. Video fields match the topic endpoint. Ordering is topic display_order/id, then video display_order/id. Summary fields: `total_videos`, `completed_videos`, `total_duration_seconds`, `completed_duration_seconds`, `remaining_duration_seconds`, `unknown_duration_videos`. Known durations are summed; only completed video durations contribute to completed time. Remaining = known total minus completed. Unknown durations are counted and excluded from time totals. Existing subjects with no videos return an empty array and zero summary.

### PATCH /api/videos/{video_id}/progress

Request: `{ "status": "not_started" | "in_progress" | "completed" }`. Extra fields, including `user_id` and `watched_seconds`, are rejected. Returns the updated video with the same fields as GET. Ownership comes exclusively from the verified token. Progress is lazily inserted on start/completion; resetting an untouched video remains derived. Repeated completion preserves completed_at; moving to in_progress clears it; reset clears all timing/viewing values. No video player or viewing-time measurement is implemented. Frontend controls await successful persistence and refresh the subject response; failures do not show optimistic completion.

## Study events

- `GET /api/study-events`
- `POST /api/study-events`
- `GET /api/study-events/{event_id}`
- `PATCH /api/study-events/{event_id}`
- `DELETE /api/study-events/{event_id}`

Candidate create payload:

```json
{
  "title": "Revenue Recognition",
  "subject_id": "uuid",
  "topic_id": "uuid",
  "event_type": "lecture",
  "start_at": "2026-10-10T19:00:00+08:00",
  "end_at": "2026-10-10T21:00:00+08:00",
  "recurrence_rule": null,
  "notes": null
}
```

## Study sessions

- `POST /api/study-sessions`
- `PATCH /api/study-sessions/{session_id}`
- `GET /api/study-sessions`

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
