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

Initial project does not require external product analytics.

Prefer first-party study analytics.

If external telemetry is added later, document provider, events, retention, controls, and sensitive-data handling.

Never send private PDF contents to analytics providers.

## Timezone

Store timestamps unambiguously and display them using the user's configured timezone.

Initial expected timezone: `Asia/Manila` unless user settings specify otherwise.
