# DATA_AND_TELEMETRY.md

## Phase 12 AI boundary

AI output is a transient suggestion, not progress. Only reviewed, explicit
question/card saves persist data, with provider/model/time and original source
IDs/pages. Provenance records draft origin rather than certifying edited content.
AI cards initially remain suspended; no recall history or active schedule is
generated. Quiz explanations use completed snapshots and cannot change grades.
No raw prompts/chat history are persisted. Verified PDF quotes/page pointers aid
source checking, without guaranteeing every generated claim. Topic-only help has
no invented PDF citations. Rate counters contain only bounded identities and
timestamps, never document content or credentials. See [AI.md](AI.md).

## Phase 11 actual-time analytics

Focus reuses persisted planner sessions. The backend owns timestamps and final
duration; the browser clock only displays elapsed time. An activity type is
explicitly selected for new sessions. Existing history stays general rather
than being classified from unrelated completion data. Pause is deferred.

Only completed sessions contribute to analytics. Selected profile-local dates
become half-open UTC boundaries, and overlapping durations are clipped and split
at local midnights. Integer seconds reconcile with the persisted floored duration.
Session count counts overlapping completed sessions once; averages and longest
use their duration inside the selected range. Empty days mean zero *recorded*
completed study time. Active/open sessions do not inflate historical metrics.

Planned totals use real expanded calendar occurrences and their edits/deletes,
excluding cancelled events but including skipped plans. Task estimates and video
lecture durations do not enter actual-time totals. Planned/actual intervals are
additive, independent totals, not an adherence score. No weighted readiness,
productivity score, streak rule or external telemetry is introduced. Detailed
rules: [Phase 11](docs/phase-11-analytics-focus.md).

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

Phase 8 grades completed snapshots server-side. Each question is worth one point;
single-select/true-false require the one correct key, multi-select requires exact
set equality. Missing/empty answers earn zero; there is no partial credit or
negative marking. The denominator is every question in the snapshot.
score_percent = score_value / total_questions * 100, decimal half-up to two places.
Answer keys/explanations/correctness stay absent from active-attempt responses.
Completed results persist with server timestamps and survive later bank/quiz
edits. Attempt history is real user data; no topic-readiness or advanced analytics
formula, generated questions, flashcards or activity telemetry is introduced.
Unsaved browser selections may use a bounded session-only recovery record containing
question ID, selected keys and their last saved baseline. It contains no prompt,
answer key, explanation or token, and is cleared on confirmed save/completion;
it is a draft, never authoritative grading or performance history.

Future aggregate candidates (not implemented in Phase 8):

- attempts
- latest score
- best score
- average score
- accuracy by subject/topic
- mistakes by topic

Use completed attempts for score aggregates unless documented otherwise.

## Flashcard metrics

Phase 9 stores canonical server review history and versioned current card state.
Again/Hard/Good/Easy are self-reported recall quality, not objective correctness or
readiness. Each accepted due-card review advances exactly once; immutable history
captures front/back, prior and next interval and server timestamps. Card edits or
archival preserve history. Exact request retries never inflate review counts.

Due counts include active cards only: overdue before the profile local-day start,
due_today from that start through now, upcoming after now. Cards later today are
not yet reviewable. Dashboard exposes overdue/due_today only, excluding future
cards; these are real queue counts, not analytics or a retention estimate.
Scheduler `recall-v1` is documented in DATABASE.md and the Phase 9 contract.
No workbook R1–R5 history, guessed ratings, source dates or topic readiness is copied.
Browser session recovery stores only owner-scoped card/request IDs, revision and
rating for an unconfirmed review. It stores no card text or credentials, retrieves
the owned card through FastAPI, and requires explicit retry rather than automatic
submission. Server confirmation clears this metadata.

Future aggregate candidates:

- cards due
- cards overdue
- reviews completed
- rating distribution
- retention proxy only when the review algorithm supports it

## Assessment metrics

Phase 10 records manual assessment results separately from planned definitions.
Known score/max_score yields server percentage; unscored results stay null. Source
checkboxes/formulas are never assessment attempts. Definition archival keeps history.
Coverage readiness displays current own video completion, graded completed quiz
snapshot answers (repeat attempts included) and active due/overdue recall. Zero
denominators display no-data, not zero performance. Selected-topic coverage is
explicit, whole-subject scope only when supplied. No weighted readiness, mastery
estimate or source checkbox progress is introduced.

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
