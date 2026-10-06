# Study Planner Implementation Plan

> **For agentic workers:** Use focused independent frontend/backend implementation, followed by integration and a fresh whole-change review. Track the steps below.

**Goal:** Implement the approved owner-scoped editable calendar, tasks and actual sessions without later-phase features.

**Architecture:** Existing SQLAlchemy repositories/FastAPI APIs persist plans and occurrence snapshots. A protected Next.js planner uses the current authenticated services and shell. Weekly recurrence is expanded server-side over bounded ranges.

**Tech Stack:** Existing FastAPI, Pydantic, PostgreSQL/Alembic, Next.js/React/TypeScript; stdlib timezone/date handling, no heavy calendar dependency.

**Spec:** [Phase 6 design](phase-6-design.md).

## Global constraints

- No secrets/source workbook or unrelated user edits committed. Preserve frontend/next-env.d.ts.
- Port 8000 belongs to F1 and must not be modified. Study Hub API is localhost:8001.
- SCHEDULE/Calendar remain report-only: zero guessed timestamps or user mappings.
- One focused commit after all checks; no intermediate commits or later phases.

## Review focus

Own IDs and owner composite foreign keys; partial/null patches; recurrence exceptions moved across date windows; local wall-clock/DST conversion; task/session race conditions and preservation after event deletion.

## Tasks

1. Database: create `backend/migrations/versions/0004_study_planner.py` with four tables, checks, indexes, owner-scoped read RLS, preserved session references and task unlink behavior. Apply and inspect through the existing environment without printing credentials.
2. Backend: create planner schemas, recurrence/validation service, scoped repository and thin API router; register router and POST/DELETE CORS methods. Add/run focused tests that first fail for missing functionality, then cover strict fields, merging/relationships, recurrence/DST/range limits and authenticated CRUD boundaries. Shared interfaces are the design's HTTP contract.
3. Frontend: add protected study-plan route, service types, date helpers, calendar/agenda, native event/task dialogs and session controls. Extend API client POST/DELETE/204 support and navigation only. Validate configured-zone date helpers then build, preserving the user's generated-file changes.
4. Integration: use real authenticated temporary users for event/task/session CRUD, isolation, scheduling atomicity, occurrence edits/deletes/series behavior, invalid relationships, RLS read isolation/browser write rejection, duration checks and API smoke on 8001. Clean up only temporary verification records.
5. Documentation/review: update DATABASE/API/IMPORTS/DATA_AND_TELEMETRY/README/ROADMAP; review safe schedule report and narrow current diff. Obtain fresh scoped code review, fix material findings and rerun covering checks.
6. Finish: scan staged files for credentials/private workbook, leave real environment files and prior user edit unstaged; commit with the user-specified message and push main without force. Report actual results/limitations.

## Progress

- [x] Source inspection, dry-run report, and approved design.
- [x] Local CORS/preflight/auth and loaded frontend API URL verified on 8001.
- [x] Schema and migration (`0004_study_planner`, RLS enabled on all four tables).
- [x] Backend and narrow checks (17 focused checks, including two review regressions).
- [x] Frontend and build (8 timezone/date checks, production build/type checks).
- [x] Live integration/security checks (two temporary users cleaned up, frontend SDK/services smoke, eight preflights).
- [x] Docs and independent review (DST/date-boundary findings fixed and independently rechecked).
- [x] Ready for focused commit and push (diff/credential scan passed; final Git outcome is reported in the completion message).
