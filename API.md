# API.md

## Purpose

Initial REST contract direction between Next.js and FastAPI. Exact schemas are finalized feature-by-feature.

## Conventions

Base prefix: `/api`

Use conventional HTTP statuses. Do not leak secrets or raw internal stack traces.

## Foundation

### GET /health

Response:

```json
{
  "status": "ok"
}
```

## Subjects

- `GET /api/subjects`
- `GET /api/subjects/{subject_id}`
- `GET /api/subjects/{subject_id}/topics`

## Topics

- `GET /api/topics/{topic_id}`

Do not invent a progress-write endpoint until the progress model is defined.

## Videos

- `GET /api/topics/{topic_id}/videos`
- `PATCH /api/videos/{video_id}/progress`

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

Frontend sends the authenticated user's bearer token for protected endpoints.

FastAPI validates identity and scopes user-owned data to that identity.

Do not trust `user_id` supplied in request bodies for ownership.
