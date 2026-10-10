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

Phase 7 scope includes private Storage originals, owner-scoped metadata/PDF page
sections, PDF text extraction and CSV validation/20-row previews (moved into this
phase by the explicit user prompt). Resource Library upload/list/filter/detail,
short-lived download/open, safe deletion and failure statuses are included.
No CSV quiz/flashcard/domain import, OCR, AI, vector search or later feature starts.

- Supabase Storage
- resources
- upload/list/filter
- PDF metadata
- CSV upload
- processing states

## Phase 8 - Quiz engine + question bank

The explicit user phase order moves the originally planned quiz engine into
Phase 8. PDF text extraction and generic CSV previews were completed in Phase 7.

Implemented scope: private manual/CSV question banks; single-select, multi-select
and true/false; subject/topic/owned-resource associations; ordered quiz builder;
frozen attempts and persisted answers; server-side exact grading; history and
review; pre-submit key protection; validated preview/confirmed idempotent CSV
import; owner RLS and restricted grading-column grants. Shared auth stays intact.
No flashcards, spaced repetition, AI/PDF-to-quiz generation, assessments or
advanced analytics.

## Phase 9 - Flashcards and recall

The explicit user phase order moves flashcards and recall into Phase 9.
Implemented: private decks/cards with curriculum/source associations, editing and
archive; active due/overdue/upcoming queues; reveal/rate flow; immutable history;
versioned backend scheduling and revision/request retry protection; manual editable
quiz-mistake conversion; real Dashboard due counts. Workbook recall stays report-only,
with 155/156 exact topic matches and no imported repetition history or invented cards.

## Phase 10 - Assessments

Private definitions, selected-topic/explicit whole-subject coverage, editable dates,
manual attempt results/history, transparent existing-progress components and
authenticated ownership/RLS. Workbook definitions/coverage use validated exact
mapping, transactional insert-only import and zero-insert reruns; missing dates,
unmatched labels and checkbox/formula results remain unimported and documented.
No AI, composite readiness formula, advanced analytics or automatic calendar writes.

## Phase 11 - Analytics and Focus Timer

The explicit user phase order brings actual-time analytics into Phase 11.
Implemented: Focus start/finish/restoration through existing persistent sessions,
single-active enforcement and server-derived duration; explicit activity types;
profile-local 7/30/90-day and bounded custom ranges; daily recorded activity,
subject/activity breakdowns, transparent planned versus actual, heatmap and
paginated session history. Existing shared auth/session UX is preserved.
Pause, productivity/readiness scores and later product phases remain deferred.

## Phase 12 - AI Study Features

The explicit user phase order brings AI assistance into Phase 12. Implemented:
backend Gemini REST adapter; bounded source retrieval and verified page quotes;
`/assistant`; editable question/flashcard drafts with explicit confirmation;
completed quiz snapshot explanations; signed original-draft provenance; secondary
resource/topic actions. AI cards save suspended. No automatic study-state writes,
embeddings, provider fallback or new SDK. Existing shared session UX is preserved.
Live Gemini verification requires backend `GEMINI_API_KEY` and `GEMINI_MODEL`;
focused mocked-provider checks cover the integration without paid API calls.

## Phase 13 - Reserved future scope (not started)

No final QA/deployment or additional product work is authorized by Phase 12.
Wait for the next explicit phase instruction.

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
