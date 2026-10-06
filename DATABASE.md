# DATABASE.md

## Purpose

Planned relational domains for CPA Study Hub. This is a design contract, not the final migration file.

## Principles

- PostgreSQL/Supabase is the structured-data source of truth.
- Use UUID primary keys unless implementation establishes another consistent convention.
- Every user-owned record needs a clear ownership path.
- Use migrations for schema changes.
- Do not mirror spreadsheet tabs directly.
- Avoid destructive migrations without explicit approval.

## Identity

### profiles

Candidate fields:

- id
- display_name
- timezone
- target_exam_date
- created_at
- updated_at

## Curriculum

### subjects

- id
- code
- name
- display_order
- color_key
- is_active
- created_at
- updated_at

Seed:

- FAR
- AFAR
- MAS
- TAX
- RFBT
- AT
- AP

### topics

- id
- subject_id
- parent_topic_id nullable
- code nullable
- title
- description nullable
- display_order
- created_at
- updated_at

Do not store user-specific completion directly on shared topic definitions.

### videos

- id
- topic_id
- title
- duration_seconds nullable
- source_url nullable
- display_order
- created_at
- updated_at

### user_video_progress

- id
- user_id
- video_id
- status
- started_at nullable
- completed_at nullable
- watched_seconds nullable
- updated_at

## Planning

### study_events

- id
- user_id
- subject_id nullable
- topic_id nullable
- resource_id nullable
- assessment_id nullable
- title
- event_type
- start_at
- end_at
- status
- recurrence_rule nullable
- notes nullable
- created_at
- updated_at

Candidate event types:

- lecture
- reading
- drill
- recall
- quiz
- assessment
- general

### study_tasks

For unscheduled/plannable work:

- id
- user_id
- subject_id nullable
- topic_id nullable
- title
- task_type
- estimated_minutes nullable
- due_at nullable
- status
- created_at
- updated_at

### study_sessions

Actual study activity:

- id
- user_id
- study_event_id nullable
- subject_id nullable
- topic_id nullable
- started_at
- ended_at
- duration_seconds
- notes nullable
- created_at

Planned duration belongs to events/tasks. Actual duration belongs to sessions.

## Resources

### resources

- id
- user_id
- subject_id nullable
- topic_id nullable
- title
- original_filename
- resource_type
- storage_path
- mime_type
- size_bytes
- processing_status
- page_count nullable
- created_at
- updated_at

Initial resource types:

- pdf
- csv

### document_sections

- id
- resource_id
- heading nullable
- page_start nullable
- page_end nullable
- sequence_number
- text
- metadata jsonb nullable
- created_at

Exact AI chunking is deferred until AI implementation.

## Questions and quizzes

### questions

- id
- user_id nullable depending on ownership model
- subject_id nullable
- topic_id nullable
- resource_id nullable
- question_type
- prompt
- explanation nullable
- source_page nullable
- source_section_id nullable
- origin
- created_at
- updated_at

Origins may include manual, csv, ai, imported.

### question_options

- id
- question_id
- option_key
- text
- is_correct
- display_order
- feedback nullable

### quizzes

- id
- user_id
- subject_id nullable
- topic_id nullable
- title
- description nullable
- created_at
- updated_at

### quiz_questions

- quiz_id
- question_id
- display_order

### quiz_attempts

- id
- user_id
- quiz_id
- started_at
- completed_at nullable
- score_value nullable
- score_percent nullable
- created_at

### quiz_answers

- id
- attempt_id
- question_id
- selected answer representation
- is_correct
- answered_at
- time_seconds nullable

Final multi-select storage representation is an implementation-phase decision.

## Flashcards and recall

### flashcard_decks

- id
- user_id
- subject_id nullable
- topic_id nullable
- title
- created_at
- updated_at

### flashcards

- id
- deck_id
- resource_id nullable
- topic_id nullable
- front
- back
- source_page nullable
- origin
- created_at
- updated_at

### flashcard_reviews

- id
- user_id
- flashcard_id
- rating
- reviewed_at
- next_review_at nullable
- interval metadata nullable
- algorithm_metadata jsonb nullable

Ratings:

- forgot
- hard
- good
- easy

Do not finalize the spaced-repetition algorithm until explicitly specified.

## Assessments

### assessments

- id
- user_id
- title
- assessment_date nullable
- status
- score_value nullable
- score_percent nullable
- notes nullable
- created_at
- updated_at

### assessment_topics

- assessment_id
- topic_id
- coverage_status nullable

## Progress and analytics

Prefer deriving progress from canonical source records rather than duplicating many counters.

Initial analytics should derive from:

- study_sessions
- study_events
- user_video_progress
- quiz_attempts / quiz_answers
- flashcard_reviews
- assessments

Do not create a composite readiness score until its formula is explicitly documented.

## Security

- scope user-owned data to authenticated users
- keep service-role key backend-only
- use RLS where applicable
- enforce storage ownership/access
