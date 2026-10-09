# DATA_AND_TELEMETRY.md

## Purpose

Defines study metrics and derived data without overbuilding analytics during foundation work.

## Canonical activity sources

- study_events — planned study
- study_sessions — actual study
- user_video_progress — lecture/video progress
- quiz_attempts / quiz_answers — quiz performance
- flashcard_reviews — recall performance
- assessments — formal checkpoints

## Planned vs actual

Planned study time derives from scheduled event/task duration.

Actual study time derives from `study_sessions`.

Do not overwrite planned time with actual time.

Phase 6 stores planned aware start/end timestamps in `study_events` and independent actual timestamps in `study_sessions`. Recurring occurrences use their expanded/snapshot schedule times, not one template duration multiplied by an invented count. Task estimates are planning inputs; a scheduled task and its linked event must not be counted twice by any later aggregation.

Active sessions have null end/duration. On stop, FastAPI captures one server timestamp and stores the floored elapsed seconds; repeated stop preserves it. Only one active session is allowed per user, and it survives browser reload. Calendar completion does not generate a session; stopping a session does not alter the event. Deleting events/series preserves actual session timestamps, duration, notes and subject/topic, while clearing deleted references. No planned/actual dashboard, composite progress or external telemetry is implemented.

Useful metrics:

- planned minutes
- actual minutes
- completion ratio
- missed/rescheduled events

## Subject progress

Subject progress requires an explicit formula.

Possible inputs:

- topic completion
- video completion
- drills
- quizzes
- recall

Do not invent weightings during unrelated implementation. Until defined, expose independent metrics rather than a misleading composite percentage.

## Video metrics

- videos completed
- total videos
- completed duration
- remaining duration

Phase 5 uses independent lecture metrics only. Completed count is the current user's `completed` rows joined to available videos. Completed lecture time sums those videos' known `duration_seconds`; remaining lecture time is total known duration minus completed duration. Unknown durations are reported separately and excluded from time sums. `in_progress` contributes no partial watch time; `watched_seconds` is not measured or writable in this phase. These values are source lecture lengths, not actual study time or a composite subject progress percentage. No workbook checkboxes are transferred to user progress.

Phase 6.5 exposes these same metrics across active subjects on Dashboard: total/completed/remaining video counts, known completed/remaining lecture duration and unknown-duration count. Per-subject topic/video/completed-video counts are independent inventory/progress values. No weighted subject score, streak, planned-vs-actual aggregation, charts or external telemetry is introduced. Today uses the profile's local-day boundaries and existing recurrence expansion; upcoming tasks are pending only, with overdue tasks first according to due-date order and undated tasks last. Reads do not manufacture events, tasks, sessions or video progress.

## Quiz metrics

- attempts
- latest score
- best score
- average score
- accuracy by subject/topic
- mistakes by topic

Use completed attempts for score aggregates unless documented otherwise.

## Flashcard metrics

- cards due
- cards overdue
- reviews completed
- rating distribution
- retention proxy only when the review algorithm supports it

## Assessment metrics

- upcoming date
- covered topics
- prerequisite study where defined
- result/score when entered

Do not claim readiness without a documented formula.

## Streak

Streak definition must be explicit before implementation.

Possible initial direction: a day qualifies when actual study reaches a configured minimum or at least one meaningful study session is completed.

Do not silently choose the threshold.

## Readiness score

Deferred.

If introduced later, document:

- inputs
- formula/weights
- UI explanation
- versioning if formula changes

## Privacy / telemetry

Phase 7 resource metadata (size, page/row count, processing status) describes the
uploaded source, not learning progress or study activity. Extracted PDF content
and CSV previews are private and owner-scoped. Processing logs use safe failure
categories and resource identifiers, never document text, CSV values, filenames,
signed URLs, tokens or provider exception payloads. No document analytics or AI
provider transmission is introduced.

Initial project does not require external product analytics.

Prefer first-party study analytics.

If external telemetry is added later, document provider, events, retention, controls, and sensitive-data handling.

Never send private PDF contents to analytics providers.

## Timezone

Store timestamps unambiguously and display them using the user's configured timezone.

Initial expected timezone: `Asia/Manila` unless user settings specify otherwise.
