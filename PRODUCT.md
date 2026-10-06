# PRODUCT.md

## Product

Working name: **CPA Study Hub**

CPA Study Hub is a personal CPALE study-management and learning platform that turns an existing structured review workflow into an interactive web application.

The existing Google Sheet is an initial migration/import source. The production application uses a real database.

## Primary goals

Help the user:

- know what to study today
- manage an editable calendar and study schedule
- track subject/topic/video progress
- keep study resources in one library
- upload supported PDF/CSV files
- take quizzes
- review flashcards
- use spaced repetition/recall
- track assessments
- view meaningful analytics
- use source-grounded AI study assistance later

## CPA subjects

Seed subjects:

- FAR — Financial Accounting and Reporting
- AFAR — Advanced Financial Accounting and Reporting
- MAS — Management Advisory Services / Management Services
- TAX — Taxation
- RFBT — Regulatory Framework for Business Transactions
- AT — Auditing Theory
- AP — Auditing Problems

## Dashboard

Should answer:

- What should I study today?
- How much progress have I made?
- What recall is due?
- What assessment is coming?
- Which subjects need attention?
- How much did I study recently?

Primary dashboard content:

- overall progress
- subject progress
- today's study plan
- recall due/overdue
- upcoming assessment
- study streak
- weekly study time
- recent resources

## Study planner and calendar

The schedule is editable.

Users can:

- create/edit/delete study events
- reschedule events
- drag/drop where supported
- mark events complete
- create recurring plans
- link events to subjects/topics/resources/assessments
- use month/week/day views
- manage unscheduled study tasks

The spreadsheet schedule may seed the first schedule, but the database becomes the source of truth.

Event types:

- lecture
- reading
- drill
- recall
- quiz
- assessment
- general study

Track **planned time** separately from **actual study time**.

## Subjects and topics

Each subject has:

- overview
- topics
- lecture/video progress
- resources
- quizzes
- flashcards/recall
- analytics

Topics are the central learning unit and may connect to videos, events, sessions, resources, questions, quizzes, flashcards, recall, and assessments.

## Videos

Track:

- title
- topic
- duration
- completion
- optional completion date

Useful summaries:

- completed/total videos
- completed/remaining watch time

## Resource library

Initial supported resources:

- text-based PDF
- CSV

Capabilities:

- upload
- classify by subject/topic
- metadata
- processing status
- generate study material later
- retain source references

Future candidates:

- scanned/OCR PDF
- DOCX
- XLSX
- images

## PDF

Initial scope:

- selectable-text PDFs
- file storage
- metadata
- text extraction
- page-aware references
- sections where detectable

Defer OCR/scanned PDFs.

## CSV

Initial import types:

1. quiz/question bank
2. flashcards
3. topics/progress where explicitly supported

Every import should support validation, preview, valid/warning/error counts, and confirmation before commit.

## Quiz system

Initial question formats:

- single-select
- multi-select
- true/false

Sources:

- manual
- CSV
- PDF/AI generated

Results should support:

- score
- answer review
- explanations
- source references
- weak-topic identification
- create flashcards from mistakes

Do not add automated free-response grading in the first version.

## Flashcards

Cards may be:

- manual
- CSV imported
- PDF generated
- created from quiz mistakes

A card may belong to a deck, subject, topic, and source resource.

Review actions:

- Forgot
- Hard
- Good
- Easy

## Recall / spaced repetition

The source spreadsheet uses repetition stages such as R1-R5.

The application should evolve this into automatic spaced repetition, but the exact algorithm must be explicitly chosen/documented before implementation.

## Assessments

Track:

- name
- date
- coverage
- subjects/topics
- status
- optional result/score

Do not create a readiness score without a documented formula.

## Analytics

Potential metrics:

- study time
- planned vs actual
- subject/topic progress
- video completion
- quiz performance
- recall performance
- assessment preparation
- streak
- completion trends

## AI assistant

Planned AI features:

- summarize supported documents
- generate questions
- generate flashcards
- explain answers
- source-grounded document Q&A
- topic tutoring

AI is not the authority for core application state.

## Out of scope for foundation

Do not implement during initial setup:

- social/community features
- payments
- marketplace
- native mobile app
- OCR
- free-response grading
- background-job infrastructure
- production AI generation

## Foundation success

Foundation is successful when:

- frontend/backend are independent directories
- architecture contracts are documented
- secrets are correctly separated
- both apps are independently runnable
- database/API ownership is clear
- future features can be added without collapsing the separation
