# Phase 6 verification

Study Hub API: localhost:8001; frontend: localhost:3001. The F1 service on port 8000 was not modified. Real environment files and the source workbook stay ignored and uncommitted.

## Schema and security

- Applied Alembic `0004_study_planner`: events, recurring occurrence snapshots, tasks and sessions.
- All four tables have owner-scoped SELECT RLS; anonymous/public access and direct browser mutations are denied. FastAPI mutations filter by the verified Auth identity.
- Live two-user checks verified event/task/session isolation and rejected cross-user mutations. Database constraints independently rejected forged owner references and mismatched topic/subject references.
- Real authenticated event CRUD, task CRUD/scheduling, occurrence edits/rescheduling/suppression, series edits and session start/stop were exercised. No passwords, tokens, account identifiers or personal notes are included here.
- Scheduling failures left tasks unchanged; a second schedule was rejected. Deleting linked events returned scheduled tasks to pending.
- One-active-session conflict, derived duration, repeated-stop idempotency and planned-time preservation passed. Deleting a series preserved finished session timestamps/duration/curriculum context and cleared deleted references.

## Frontend and local connection

- Actual frontend SDK signed in, sent the bearer token through the existing frontend API modules to FastAPI/PostgreSQL, and exercised GET/POST/PATCH/DELETE including 204 handling. Signed-out requests were rejected.
- Loaded development client configuration uses API port 8001; no stale port-8000 API URL was detected.
- GET /health, authenticated /api/auth/me and frontend /study-plan route smoke passed. Eight OPTIONS checks covered GET/POST/PATCH/DELETE from localhost:3000 and localhost:3001; unapproved origin was rejected.
- Final frontend production build/type validation passed with /study-plan included. Eight focused configured-timezone/date helper checks passed, including fractional offsets, DST gaps/folds and calendar arithmetic.
- No interactive browser automation was performed. Native dialog and responsive agenda behavior were reviewed in code; the build/route/API/service checks do not claim visual browser QA.

## Recurrence review

Seventeen focused backend checks passed. Independent review found two edge cases: unrelated DST-gap dates interfering with a requested window, and extreme calendar arithmetic escaping as an uncaught exception. Both were fixed using observed failing regression checks, then independently rechecked: adjacent nonoverlapping days load, actual invalid DST occurrences return 422, and unrepresentable date arithmetic returns sanitized 422. No important review findings remain.

Changing timezone or removing recurrence is deliberately rejected after snapshots exist. Series edits preserve individual snapshots; untouched occurrences remain virtual. Weekly selected weekdays and optional inclusive local UNTIL are a documented subset, not a full recurrence engine.

## Source and cleanup

The reproducible SCHEDULE/Calendar inspection proposes zero inserts/updates. Its safe report preserves source layout/conflicts without personal calendar labels. No workbook completion states or source schedules were imported.

Both temporary verification accounts and their records were removed. The frontend smoke task was deleted. Post-check database counts: 7 subjects, 163 topics, 1,562 videos; zero verification events, occurrence snapshots, tasks or sessions remain. No existing curriculum or user activity was deleted.

Deferred: source schedule import pending exact times/ownership and ambiguous references, drag-and-drop, separate Day grid, advanced timers, resources/assessments linkage and every later roadmap domain. No dependencies were added.
