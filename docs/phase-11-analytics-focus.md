# Phase 11 — Analytics and Focus

## Design and implementation contract

Reuse the existing owner-scoped planner session start/stop transaction, partial
unique active-session index and server timestamps. Add only an `activity_type`
column: lecture, reading, practice, recall, quiz or general. Existing sessions
remain general; no historical activity is inferred. Pause is deferred.

Focus restores the persisted active session, reads a server clock anchor, and
displays elapsed time without allowing the client to submit duration. Starting
requires an explicit user action. Subject/topic/event association follows current
planner validation. A conflicting start refreshes the active session. Stopping
is retry-safe and does not complete or alter a planned event.

## API contract

- GET `/api/focus`: `{timezone, server_now, active_session, today_seconds,
  today_session_count, recent_sessions}`. Recent completed sessions are bounded
  to ten and include subject code/title and topic title. Session DTOs retain
  current fields plus activity_type.
- POST `/api/study-sessions`: existing request plus optional activity_type
  (default general). PATCH stop remains unchanged.
- GET `/api/analytics/summary?period=7|30|90`: one structured response with
  profile timezone, inclusive local start_date/end_date, summary metrics, daily
  activity, subject/activity breakdowns and planned versus actual.
- GET `/api/analytics/sessions?period=7|30|90&limit=20&offset=0`:
  `{sessions,total,limit,offset}`. Sessions include curriculum labels. Limit
  maximum 100. Custom ranges may use paired start_date/end_date, maximum 90
  inclusive days and no future end date; invalid/partial ranges return 422.

Summary shape: `{timezone,start_date,end_date,summary,daily,subjects,activities}`.
`summary`: total_seconds, session_count, active_days, average_session_seconds,
longest_session_seconds, planned_seconds.
`daily`: `{date,duration_seconds,session_count}`.
`subjects`: `{subject_id,subject_code,subject_title,subject_color_key,duration_seconds,
session_count,planned_seconds}`; unassigned context uses null identifiers.
`activities`: `{activity_type,duration_seconds,session_count}`.

## Calculation rules

Only finished sessions enter actual-time metrics. Clip intervals to the selected
profile-local date range, split across local midnights (including DST), and retain
integer-second reconciliation with persisted duration. Count sessions overlapping
the range once; average/longest use their time inside that range. Days with no
recorded completed activity are zero recorded seconds, not invented activity.

Planned time uses the existing recurrence expansion and occurrence edits/deletes;
clip intervals to the same boundaries. Exclude cancelled events, retain scheduled,
completed and skipped plans. Task estimates are excluded to avoid double counting.
Subject comparisons show independent additive planned and actual totals, without
an adherence/readiness score. Open sessions are shown in Focus but excluded from
historical aggregates until finished. All SQL is scoped to the verified user.

## Frontend

Preserve the shared authenticated layout. `/focus` presents the active timer or
a compact subject/topic/activity/event selector, today's actual totals and recent
sessions. Add subject/topic quick-start links (prefilled, never auto-start).
`/analytics` presents period controls, compact metrics, a daily duration chart,
subject/activity breakdowns, planned versus actual, a calendar heatmap and
paginated session history. Use existing charcoal tokens, restrained borders and
subject accents; no new chart dependency or decorative dashboard redesign.

## Validation and completion

Focused tests cover session activity validation, clipping/date boundaries,
recurrence planning, aggregation and ownership. Live checks use temporary users
and synthetic records only: start/restore/conflict/finish/retry, no client duration,
owner isolation/RLS and exact analytics fixtures. Clean fixtures/users afterward.
Run frontend build/type and route smoke checks. Review the Phase 11 diff, exclude
the pre-existing next-env.d.ts edit, secrets and private inputs; commit once with
`feat: add study analytics and focus timer`, then push main. No Phase 12 work.
