# Phase 6: editable calendar and study planner

The approved goal is an owner-scoped planner backed by FastAPI/PostgreSQL, preserving Phases 1–5. The local frontend is localhost:3001 and Study Hub API is localhost:8001; port 8000 belongs to another project.

## Data and recurrence

- `study_events` stores one-off events or weekly series, with subject/topic, title, type, aware start/end timestamps, IANA timezone, status, notes, and timestamps.
- `study_event_occurrences` stores full snapshots only when a recurring occurrence is edited, completed, deleted, or used for a session. Its identity is `(study_event_id, occurrence_date)` in the series timezone. `is_deleted` suppresses just that occurrence. Unmodified occurrences are virtual, expanded only for bounded requested ranges.
- Weekly rules use the documented subset `FREQ=WEEKLY;BYDAY=MO,WE;UNTIL=20261231`. UNTIL is an optional inclusive local date, not a full RFC5545 engine. The anchor date must be selected. Local wall-clock times are preserved; invalid/ambiguous DST times are rejected when creating/rescheduling and reported rather than guessed during expansion.
- A series edit affects unmodified occurrences; snapshots remain independent, including ones whose original weekday was removed. With saved snapshots, changing timezone or removing recurrence returns 409 to preserve their identity; create a new series instead. Series deletion removes its schedule/occurrences but preserves sessions by detaching their references. Recurring series status remains scheduled; statuses are changed per occurrence.
- `study_tasks` stores pending/scheduled/completed/cancelled work. Its optional `scheduled_event_id` links to its own event. Scheduling locks the task and atomically creates an event and updates the task. Deleting the event unlinks it and returns scheduled tasks to pending.
- `study_sessions` stores actual server-timestamped activity, with optional own event and occurrence references. Only one unfinished session per user. Stop derives integer duration from timestamps and is idempotent. Completing an event does not fabricate actual time; stopping a session does not change planned time.
- All four tables are user-owned. References enforce owner and topic/subject consistency. Authenticated browser roles have owner-scoped read access only; mutations use FastAPI and scoped repositories. No resource/assessment tables or speculative linkage fields.

## Shared HTTP contract

All ownership comes from the verified bearer token. Extra request fields, including user_id, are forbidden. Unknown/other-owner IDs return 404; invalid values/relationships return 422; conflicting scheduling/active session returns 409; infrastructure failures return sanitized 503.

Event fields: `id, subject_id, topic_id, title, event_type, start_at, end_at, timezone, status, recurrence_rule, notes, created_at, updated_at`. IDs are UUIDs; optional associations/rules/notes are null. Event types: lecture, reading, drill, recall, quiz, assessment, general. Event statuses: scheduled, completed, skipped, cancelled.

- `GET /api/study-plan/context`: `{timezone, active_session}` from profile/own unfinished session.
- `GET /api/study-events?start_at=...&end_at=...`: overlapping occurrence list; aware timestamps, positive range at most 93 days. Each row adds `occurrence_date` (null for one-off), `is_recurring`, and optional `occurrence_id`. Recurring row `id` is the series ID. Maximum 2000 results; overflow is rejected, not silently truncated.
- `POST /api/study-events`: event fields excluding generated IDs/timestamps. Required title/start/end; default general/scheduled and profile timezone. `GET/PATCH/DELETE /api/study-events/{id}` operates on one event or an explicitly selected series. PATCH merges before full validation. DELETE returns 204.
- `PATCH/DELETE /api/study-events/{id}/occurrences/{YYYY-MM-DD}` operates on one valid occurrence. PATCH accepts the editable event fields except recurrence_rule/timezone. DELETE creates a suppression snapshot and returns 204.
- `GET/POST /api/study-tasks`; `PATCH/DELETE /api/study-tasks/{id}`. Task fields: id, subject_id, topic_id, title, task_type, estimated_minutes, due_at, status, scheduled_event_id, created_at, updated_at. Task types match event types; pending is default. Scheduled is not client-settable.
- `POST /api/study-tasks/{id}/schedule`: EventCreate body; returns the created event. The event must retain the task's subject/topic; rejection leaves both unchanged.
- `GET /api/study-sessions`: newest first, at most 100, optional aware range filters. `POST`: optional study_event_id, occurrence_date, subject_id, topic_id, notes. Event-linked sessions inherit event context, including a snapshot for recurrence. Response: id, study_event_id, occurrence_id, subject_id, topic_id, started_at, ended_at, duration_seconds, notes, created_at.
- `PATCH /api/study-sessions/{id}`: `{action:"stop", notes?:...}` or notes alone. Active end/duration are null; finished duration is derived, never client-writable.

## Frontend

Protected `/study-plan` reuses the existing shell/Auth/API services and subject palette. Calendar Month/Week and Today/Tasks tabs use compact rows, thin borders, readable labels, and mobile agenda fallback. Click date/time to add and event to edit. A reusable native dialog provides title, subject-filtered topics, date/times, type, recurrence weekdays/end date, notes and occurrence status. Recurrence controls explicitly separate occurrence vs series. Local date/time inputs are converted using the configured timezone; invalid/ambiguous times show errors. Mutations update only after API success. Tasks support create/edit/complete/schedule; active session state survives reload and can be stopped outside the originating event.

No calendar library, drag/drop, advanced timer, fake records/metrics, notifications or later-phase features. Missing/failed data has intentional loading/error/empty states. Native dialog supplies focus containment/restoration and all controls have labels/focus styles.

## Workbook and verification

The inspected workbook/report remains authoritative: no exact study times, ambiguous source references and no chosen account. SCHEDULE/Calendar stay report-only, with zero inserts. The source workbook, real environments, private labels, and temporary artifacts stay out of Git.

Verify migrations/constraints/RLS, authenticated CRUD and ownership, relationships/range/recurrence, task scheduling, session snapshots/durations, frontend build and real service smoke. Use temporary verification records/accounts only; retain existing user data. Commit only verified Phase 6 code/docs/safe report with `feat: add study planner and calendar`, then push origin/main.
