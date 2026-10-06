# ROADMAP.md

## Principle

Build in phases. Do not build the entire platform in one Codex pass.

## Phase 0 — Documentation

Prepared before implementation:

- AGENTS.md
- PRODUCT.md
- DESIGN.md
- DESIGN_GUIDELINES.md
- ARCHITECTURE.md
- DATABASE.md
- API.md
- IMPORTS.md
- AI.md
- DATA_AND_TELEMETRY.md
- DEPLOYMENT.md
- GIT_WORKFLOW.md
- ROADMAP.md
- README.md
- CODEX_PROMPTS.md

## Phase 1 — Repository foundation

Create:

- `frontend/`
- `backend/`
- `docs/`
- `data/imports/`
- `data/templates/`
- `data/seed/`
- `scripts/`

Frontend:

- Next.js
- TypeScript
- Tailwind
- minimal app shell
- environment example

Backend:

- FastAPI
- config
- `/health`
- CORS
- project structure
- environment example

Root:

- `.gitignore`
- README
- local development instructions

No product features yet.

## Phase 2 — Database and authentication foundation

- Supabase configuration
- migrations
- profiles
- subjects
- topics
- auth validation
- seed subjects

## Phase 3 — Subject system

Implemented: authenticated active-subject list/detail, flat topic APIs, protected subject routes, cycle-safe topic display, and loading/error/empty states. Topics may remain empty until a separately authorized import. No progress formula or metrics are introduced.

- subject list/detail
- topic hierarchy
- APIs
- frontend subject pages
- only defined progress metrics

## Phase 4 — Spreadsheet migration and real curriculum import

Completed under the user-directed phase order: inspected Project 1.xlsx, imported 163 real curriculum topics through a validated dry run and insert-only transaction, and verified a zero-insert second dry run. No schema or frontend changes. Video, recall, schedule/calendar, and assessment mappings remain reports only; incomplete FAR-19/FAR-36 rows are excluded.

- workbook mapping
- dry-run importer
- subject/topic/video migration
- schedule mapping
- assessment mapping
- recall mapping report

## Phase 5 — Video tracking

Implemented: shared videos and owner-scoped progress with RLS, confirmed workbook duration parsing, transactional insert-only lecture migration, authenticated reads/status updates, and compact subject Videos pages with real summaries. Workbook completion states are excluded. FAR Vids rows 586–587 remain unresolved source conflicts requiring client/source clarification. Later phases remain deferred.

- videos
- user progress
- video UI
- duration/progress summaries

## Phase 6 — Calendar and study planner

Implemented: owner-scoped events/tasks/sessions plus minimal recurring occurrence snapshots, authenticated CRUD and atomic task scheduling, Month/Week calendar with Today/Tasks and mobile agenda, reusable event editor, weekly selected-day plans with optional end date, and reload-safe start/stop sessions. RLS and API ownership are enforced; planned and actual time stay separate. SCHEDULE/Calendar inspection remains report-only with zero writes because exact times/ownership and several source relationships are unresolved. Drag/drop, separate Day grid, advanced timer and later phases remain deferred.

- study_events
- study_tasks
- study_sessions
- month/week/day
- add/edit/delete/reschedule
- recurring events
- planned vs actual
- unscheduled tasks

## Phase 6.5 — Dashboard refresh

Implemented: a compact real-data Dashboard with profile-timezone Today events, recurring occurrences, next five pending tasks by due date (undated last), active subject topic/video/completion counts and independent lecture count/duration totals. One authenticated read-only summary endpoint avoids downloading all topic/lecture lists. The shared auth layout persists; page refresh retains existing content. Unknown durations remain explicit; no composite percentages, analytics, new schema/dependencies or Phase 7 features are added. Quick actions use existing Study Plan, Subjects and Videos routes; foundation copy is removed.

## Phase 7 — Resource library

- Supabase Storage
- resources
- upload/list/filter
- PDF metadata
- CSV upload
- processing states

## Phase 8 — PDF and CSV processing

- text PDF extraction
- page/section references
- CSV preview/validation
- quiz CSV import
- flashcard CSV import

No OCR yet.

## Phase 9 — Quiz engine

- questions/options
- quizzes
- attempts/answers
- scoring
- explanations
- results
- mistake review

## Phase 10 — Flashcards and recall

- decks/cards
- review history
- due queue
- spaced-repetition algorithm after explicit algorithm decision
- cards from quiz mistakes

## Phase 11 — Assessments

- CRUD
- coverage
- calendar integration
- results

## Phase 12 — Analytics

- study time
- planned vs actual
- video completion
- quiz metrics
- recall metrics
- assessment metrics
- subject analytics

No readiness score until formula is defined.

## Phase 13 — AI

- provider abstraction
- Gemini integration
- document summarization
- source-grounded Q&A
- quiz generation
- flashcard generation
- explanations
- limits/error states

## Phase 14 — Polish

- responsive review
- accessibility
- states
- performance
- design consistency

## Phase 15 — Production deployment

- Supabase production configuration
- Vercel backend
- Vercel frontend
- variables
- CORS
- migrations
- manual smoke verification

## Future

- OCR/scanned PDFs
- DOCX/XLSX imports
- worker/background queue
- notifications
- native mobile app
- advanced readiness model
- gamification
