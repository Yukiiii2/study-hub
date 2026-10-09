# Study Hub

Study Hub is a focused study-management and learning workspace. Its current primary use case is CPALE review. The repository now implements **Phase 7 - Resource Library and file processing**, following the user-directed phase order. Sign-in, curriculum, private video progress, owner-scoped plans/sessions and private resources use the configured Supabase project.

## Repository and architecture

```text
study-hub/
|-- frontend/          # Independent Next.js application
|-- backend/           # Independent FastAPI application
|-- docs/              # Reserved for additional documentation
|-- data/
|   |-- imports/
|   |-- templates/
|   `-- seed/
|-- scripts/
|-- AGENTS.md
|-- README.md
|-- .gitignore
`-- .env.example
```

Existing specification files remain at the root to preserve their references. Repository and local folder names remain `study-hub`; the product name is **Study Hub**. Older specifications use the working name CPA Study Hub.

The frontend owns presentation, routing, accessibility, and browser interaction. FastAPI owns application APIs, validation, business logic, and future privileged data access. Next.js does not replace the backend. Neither application requires the other to start.

Current stack: Next.js App Router, React, TypeScript, Tailwind CSS, and the official Supabase JavaScript client; Python, FastAPI, Pydantic, pydantic-settings, Uvicorn, HTTPX, SQLAlchemy, Alembic, Psycopg, pypdf and python-multipart. Supabase PostgreSQL/Auth/Storage are integrated. File metadata and processing remain FastAPI responsibilities.

Frontend source is grouped into `src/app`, `src/components`, `src/features/auth`, `src/features/dashboard`, `src/features/subjects`, `src/lib`, `src/services`, and `src/styles`. Authentication helpers are separate from FastAPI clients. Backend code lives in `app/api`, `app/core`, `app/db`, `app/repositories`, `app/schemas`, and `app/main.py`; migrations live in `backend/migrations`. Additional folders will be added when actual features need them.

## Prerequisites

- Node.js 20.9+ and npm (a supported Node.js LTS release is recommended)
- Python 3.11+ and pip
- Git

Commands below run from the indicated directory. In PowerShell, use `npm.cmd` if execution policy blocks `npm.ps1`.

## Frontend development

From the repository root:

```powershell
cd frontend
Copy-Item .env.example .env.local
npm.cmd ci
npm.cmd run dev -- --port 3001
```

Open http://localhost:3001. For a production compile, use `npm.cmd run build`, then `npm.cmd start` to serve it locally.

`frontend/.env.local` is the frontend environment file:

```text
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=
```

Set `NEXT_PUBLIC_API_URL=http://localhost:8001` and configure the Supabase project URL and current publishable key (`sb_publishable_...`) in `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`. Legacy anon keys are not used. Only public values belong in this file; never put secret, database, or AI keys in frontend code or variables. Restart the dev server after changing environment values. Port 8000 belongs to another local project and must remain untouched.

## Backend development

From the repository root, on Windows PowerShell:

```powershell
cd backend
python -m venv .venv
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

Using the virtual environment's Python directly avoids requiring activation or a PowerShell policy change. Optional activation: `.\.venv\Scripts\Activate.ps1`.

On macOS/Linux:

```sh
cd backend
python3 -m venv .venv
source .venv/bin/activate
cp .env.example .env
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

`backend/.env` is loaded by centralized settings. Operating-system environment variables take precedence. Its example contains:

```text
SUPABASE_URL=
SUPABASE_SECRET_KEY=
DATABASE_URL=
GEMINI_API_KEY=
CORS_ORIGINS=
```

Configure `SUPABASE_URL`, `SUPABASE_SECRET_KEY`, and `DATABASE_URL` using the same Supabase project as the frontend. Leave `GEMINI_API_KEY` blank. Set `CORS_ORIGINS=http://localhost:3000,http://localhost:3001` for both local frontend ports. Settings read `backend/.env` by absolute path; process environment overrides the file. The value is split on commas, whitespace is trimmed, and blank entries are discarded. An empty value allows no cross-origin browser access; wildcards are rejected. Production must list only its actual trusted frontend origins. CORS permits GET, POST, PATCH and DELETE; middleware handles OPTIONS preflight with explicit origin/header checks. Changing a cached backend setting requires a server restart.

Health endpoint: GET http://localhost:8001/health returns HTTP 200:

```json
{"status":"ok"}
```

Interactive API documentation is available at http://localhost:8001/docs. Health confirms the application is running, not database connectivity. If CORS fails locally, check `/openapi.json` identifies **Study Hub API**, rather than another project's server on a different port.

The root `.env.example` only points to application-specific files; no root environment file is needed. All real environment files, virtual environments, dependencies, and build outputs are Git-ignored. Example files are tracked.

## Supabase setup and migrations

Use an existing hosted Supabase project or your own separately configured local Supabase instance. A plain PostgreSQL database alone is insufficient: the migrations require Supabase's `auth.users`, `auth.uid()`, and `anon`/`authenticated` roles. No external project is created automatically.

Obtain the project URL and current publishable key from Supabase project settings. Obtain the backend-only current secret key (`sb_secret_...`) and PostgreSQL connection string separately. Use the Connect panel's direct or session-pooler connection for migrations; the session pooler is useful on IPv4 networks. `DATABASE_URL` accepts `postgresql://...` or `postgresql+psycopg://...`. Copy the actual connection details, URL-encode special characters in the database password, and require TLS for hosted connections with `?sslmode=require`. Use the Connect panel's transaction-pooler URL for a serverless backend if appropriate; the driver disables prepared statements and application pooling. Never put credentials in examples or terminal output; real values belong only in the two Git-ignored application environment files.

From `backend/`, after setting `backend/.env`:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic current
```

`upgrade head` applies foundation, subject seed, video tracking and planner migrations (through `0004_study_planner`). It creates `profiles`, `subjects`, `topics`, `videos`, `user_video_progress`, `study_events`, `study_event_occurrences`, `study_tasks`, and `study_sessions` (plus Alembic's version table). The seed inserts FAR, AFAR, MAS, TAX, RFBT, AT, and AP with stable UUIDs and order 1-7. Re-running upgrades does not duplicate data. Curriculum/video imports run separately; no sample plans or progress are seeded. Migrations are hand-authored; create the next reviewed migration with `python -m alembic revision -m "description"`. Automatic ORM schema generation is not used. Destructive downgrades deliberately fail.

Without credentials, inspect the migration chain and generated SQL:

```powershell
.\.venv\Scripts\python.exe -m alembic history
.\.venv\Scripts\python.exe -m alembic upgrade head --sql
```

Offline generation does not apply or prove the SQL against a live database. See [DATABASE.md](DATABASE.md) for constraints and RLS. A database trigger creates one profile per Auth user and backfills existing users; the default timezone is `Asia/Manila`.

## Authentication flow

Enable email/password authentication in Supabase. Create a test account through the Supabase Dashboard's Authentication > Users interface and ensure it is confirmed/enabled. This phase provides sign-in only; there is no sign-up or password-reset UI.

Open `/login`, sign in, and return to `/`. The official SDK persists and refreshes the browser session. One root auth provider verifies the initial session with FastAPI and caches that identity in memory. Dashboard, Study Plan, Subjects, and Videos share the `(app)` layout and keep their shell mounted across navigation. Repeated same-token focus notifications reuse verification; token refresh and user updates revalidate in the background while keeping authenticated content visible. Only the initial unknown/unverified session uses the centered bootstrap skeleton. Unauthenticated sessions redirect to `/login`; sign-out and account changes clear cached identity immediately. Session persistence uses browser local storage, not server cookies, so the Next.js page guard is a client guard. Every protected FastAPI endpoint independently enforces authentication; do not use the client guard as authorization for future server-side data.

`src/services/api.ts` obtains the current session and sends `Authorization: Bearer <access_token>` to FastAPI. It never queries application tables through the browser SDK. FastAPI validates each token with Supabase's `/auth/v1/user` endpoint; `/api/auth/me` returns only the verified UUID and email. `/api/subjects` reads the database through the backend repository. Missing/invalid sessions return 401, while unavailable/unconfigured services return sanitized 503 errors. `/health` remains public and independently runnable without Supabase credentials.

On a rejected token, the API client uses SDK session recovery/one shared refresh and retries once before clearing a genuinely rejected session. Temporary service/refresh failures retain the current UI with a retry action; late requests cannot clear a replacement account/session. Focused regressions from `frontend/`: `node tests/auth-session.cjs`, `node tests/auth-api.cjs`, and `node tests/auth-render.cjs`. Optional live auth verification from the root: `node scripts/verify_frontend_auth.cjs`; it uses existing ignored verification credentials, prints no secrets, and performs no application-data writes. Rendering/focus-event regressions do not replace a manual browser check of alt-tab, navigation, and persisted storage.

The shared header shows the authenticated account and sign-out action. The Dashboard loads its real study summary through the protected `/api/dashboard` endpoint, described below.

Narrow backend checks (mocked Supabase and database boundaries):

```powershell
cd backend
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_auth_foundation.py -v
```

Live verification after setup: sign in, reload to check session persistence, browse the seven seeded subjects, sign out, and confirm `/` redirects to `/login`. Confirm protected endpoints return 401 without a bearer token. Never paste real tokens into tracked files.

## Dashboard (Phase 6.5)

The home route shows today's real events in the profile timezone (including recurring occurrences), the next five pending tasks ordered by due date with undated tasks last, lecture completion counts/known duration totals, and compact subject rows with topic/video/completed-video counts. Continue Videos opens the first subject with an in-progress lecture, otherwise the first with unfinished lectures in curriculum order. When everything is complete, Browse Videos remains available. Study Plan, Subjects and each subject's Topics/Videos links use implemented routes only.

One authenticated `GET /api/dashboard` request replaces per-subject topic/video downloads. FastAPI reads a consistent, read-only PostgreSQL snapshot, scopes progress/tasks/events to the verified user, and reuses the planner's occurrence expansion. Empty schedules/tasks are shown honestly. Unknown video durations are counted separately and excluded from time totals; lecture duration is not measured study time or composite subject progress. No fake percentages, charts, schema changes, new dependencies or later-phase features are introduced.

The existing shared auth layout stays mounted. Dashboard loading is confined to page content; Refresh retains loaded data while requesting current values and shows a retryable error on failure. Navigating back to Dashboard loads current data again. Desktop places Today/tasks beside the lecture summary; narrow screens put Today and tasks first in one column. Outdated foundation copy and the subject-setup check are removed.

Focused checks: `python -m unittest tests.test_dashboard` from `backend/`, `node tests/dashboard-render.cjs` and `npm.cmd run build` from `frontend/`. Optional read-only live comparison from the root: `node scripts/verify_frontend_dashboard.cjs`. It uses existing ignored verification credentials, compares every subject's counts/durations and today's events/pending tasks against existing APIs, renders the actual dashboard with that response, and checks implemented route responses on port 3001. It saves no private payloads and prints no credentials. Browser focus/navigation flicker still needs a manual browser observation when browser tooling is unavailable.

## Subjects and topics (Phase 3)

Open `/subjects` after signing in to browse active subjects from FastAPI. Each compact row links to `/subjects/[subjectId]`, showing the subject name and real curriculum topics. UUID routes use database identities; no frontend subject list is hardcoded. Subject accents use `color_key` presentation metadata (blue, indigo, purple, amber, rose, teal, green), falling back to the application accent when absent or unknown.

Topics use the existing `parent_topic_id` hierarchy with ordered, indented rows. Empty subjects show an intentional explanation that curriculum topics will appear after import/setup. Loading, retryable service errors, and unavailable-subject states are included. All data uses the existing authenticated API client and client guard; FastAPI independently verifies bearer tokens. No new schema, dependencies, sample topics, or progress metrics are introduced.

Read endpoints: `/api/subjects`, `/api/subjects/{subject_id}`, `/api/subjects/{subject_id}/topics`, and `/api/topics/{topic_id}`. See [API.md](API.md) for fields, flat topic response shape, ordering, and status codes.

Narrow checks from each application's directory:

```powershell
# backend/
.\.venv\Scripts\python.exe -m unittest tests.test_curriculum tests.test_auth_foundation
# frontend/
node tests/topic-hierarchy.cjs
npm.cmd run build
```

The hierarchy fixtures are isolated test data; they never populate the application database. Live Phase 3 verification reads the seven seeded subjects and their actual topic records, including the valid zero-topic state. Browser automation is not part of these checks.

## Video / lecture tracking (Phase 5)

Open a subject and choose **Videos** at `/subjects/[subjectId]/videos`. Lectures use real imported titles, grouped by the existing cycle-safe topic order, with readable durations and compact controls for Not started, In progress, and Completed. Controls await backend persistence and refresh the real summaries; failures retain the prior displayed state and offer retry. Loading, missing-subject, no-video, and no-lectures-for-topic states are included. There is no video player.

Summaries show completed/total videos and completed/remaining lecture duration for the signed-in user. Duration is not measured study time. Missing progress derives Not started; start/completion lazily stores user-owned progress. No workbook checkboxes are transferred. Backend queries explicitly scope progress by verified UUID; RLS restricts browser reads to the owner and denies browser writes.

The video importer uses the existing local XLSX dependency and Phase 4 parsing/planning architecture. From `backend/`, apply `python -m alembic upgrade head`, run `python -m app.services.video_import`, review the report, then use explicit commit mode as documented in [IMPORTS.md](IMPORTS.md). The import accepted 1,562 videos and a second dry run reports zero inserts. FAR Vids rows 586–587 remain excluded duplicate-title/different-duration source conflicts. See [video dry run](data/imports/reports/project-1-video-dry-run.md), [migration verification](data/imports/reports/project-1-video-migration.md), and [second dry run](data/imports/reports/project-1-video-second-dry-run.md).

Endpoints: GET `/api/topics/{topic_id}/videos`, GET `/api/subjects/{subject_id}/videos`, PATCH `/api/videos/{video_id}/progress`. See [API.md](API.md) and [DATABASE.md](DATABASE.md). Focused checks: `python -m unittest tests.test_video_import tests.test_videos` from `backend/`, and `npm.cmd run build` from `frontend/`. Import checks require the local ignored source workbook. No new dependencies are introduced.

## Calendar and study planner (Phase 6)

Open **Study Plan** at `/study-plan`. Month and Week calendars let you select a date/time to add an event, or select an event to edit, reschedule, complete or delete it. Today lists current events; mobile uses a readable agenda. The native editor filters topics by subject and displays the configured profile timezone. Rescheduling uses the editor; drag-and-drop and a separate Day grid are deferred.

Weekly plans support selected weekdays and an optional inclusive end date. Choose **Only this occurrence** or **Entire recurring series** when editing. Untouched occurrences are expanded on reads; individual edits/completion/deletion/session starts store snapshots. Series edits retain those snapshots. Changing timezone or converting to a one-off is rejected once snapshots exist; create a new series instead. Invalid or ambiguous DST times require another time rather than a guess.

Tasks support create/edit/complete/cancel/reopen/delete and an atomic **Schedule** action. Deleting a linked event returns scheduled tasks to pending. Reopening a linked task unlinks it while keeping its calendar event. Start a study session from an event or the planner, then stop it to save actual time. One active session is allowed per account and survives reload. Completing a plan does not create actual time; deleting a plan preserves session history.

Workbook SCHEDULE and Calendar remain report-only: no exact study start/end times or reliable ownership are supplied. Run `.\.venv\Scripts\python.exe -m app.services.schedule_inspect` from `backend/` with the existing import requirements. See the [safe schedule dry run](data/imports/reports/project-1-schedule-dry-run.md). No personal schedule/progress is imported.

Focused validation: `python -m unittest tests.test_planner` from `backend/`; `node tests/planner-dates.cjs` and `npm.cmd run build` from `frontend/`. Explicit live verification from the root: `.\backend\.venv\Scripts\python.exe scripts/verify_study_planner.py --run`. It requires the real ignored application environments, creates two temporary confirmed Auth users, verifies ownership/CRUD/recurrence/tasks/sessions/RLS and removes only those accounts. It prints no credentials. Do not run it against an unintended project. Optional `node scripts/verify_frontend_planner.cjs` checks the actual frontend SDK/services and cleans up its own task; it requires existing `PHASE2_VERIFY_EMAIL`/`PHASE2_VERIFY_PASSWORD` in the ignored backend environment and never prints them.

## Current scope and deferrals

Phase 4 adds a local, dry-run-first XLSX importer and populates 163 real topics in the existing schema. It does not change the Phase 3 frontend or API shape. Start with `backend/.venv/Scripts/python.exe -m pip install -r backend/requirements-import.txt`, then run the CLI from `backend/` as documented in [IMPORTS.md](IMPORTS.md). The expected workbook is `data/imports/Project 1.xlsx` and remains uncommitted. Commit mode requires a reviewed dry-run manifest, validates the current source/database under locks, and inserts transactionally without updates or deletes. A second dry run must report zero inserts and 163 unchanged topics for this workbook.

Safe Phase 4 reports: [initial dry run](data/imports/reports/project-1-dry-run.md), [migration result](data/imports/reports/project-1-migration.md), and [second dry run](data/imports/reports/project-1-second-dry-run.md). The two missing FAR topic titles and ambiguous hierarchy remain documented. Phase 5 resolves video duration/case mappings with explicit client-confirmed rules. Workbook recall, schedule/calendar and assessments remain report-only; Phase 6 provides user-created planner tables without a source schedule import. Generated JSON plans stay local.

Narrow importer checks from `backend/`: `.\.venv\Scripts\python.exe -m unittest tests.test_curriculum_import`. These use isolated temporary workbook fixtures and do not write to Supabase.

The dark shell remains intact; Dashboard, Study Plan, Subjects, Videos and Library are functional. The sidebar identifies only later features as planned. RLS permits own-profile reads/updates and authenticated curriculum reads, with no normal-user curriculum writes. Direct backend database credentials can bypass RLS: verified identity and explicit user scoping remain mandatory for user-owned repositories.

Intentionally deferred: subject/topic editing, generic domain imports, video playback/viewing-time measurement, schedule import, drag-and-drop, advanced timers, quizzes, flashcards/recall, assessments, analytics, and AI. There are no fake study metrics or charts.

## Resource Library (Phase 7)

Open `/library` to upload and browse private PDF/CSV resources, filter by type or
subject, search title/filename and open paginated metadata/content detail. Upload
offers optional title/subject/topic; the topic must belong to the selected subject.
Files are limited to 4 MiB and checked by type/content. PDFs expose ordered extracted
page text; CSV exposes headers, total data-row count and the first20 rows only.
No-text/unreadable PDFs retain originals with an explicit failed status; no OCR.
Open/download uses short-lived signed links, and deletion is confirmed in the UI.

From `backend/`, install `requirements.txt`, run `python -m alembic upgrade head`,
then `python -m app.services.resource_storage` to create/verify the private study-resources
bucket. Existing backend Supabase URL/secret key/database configuration suffices;
real values stay in ignored env files. See DEPLOYMENT.md for permissions and limits.
The browser does not directly write resource metadata or Storage objects.

Focused live checks from the root: `backend/.venv/Scripts/python.exe scripts/verify_resources.py --run`.
This explicitly creates two temporary Auth accounts and synthetic files in memory,
checks authenticated lifecycle/RLS/Storage isolation, then removes only its own
verification resources/accounts. No uploaded PDF/CSV fixture, credentials or
private document content is printed or committed. A future worker is deferred;
CSV quiz/flashcard imports, AI, embeddings and all Phase 8 features remain deferred.

## Git and deployment

Repository: https://github.com/Yukiii2/study-hub.git. Early solo work uses `main`, with one focused commit per completed phase. Review diffs and secrets before staging; never commit real `.env` files or rewrite remote history. See [GIT_WORKFLOW.md](GIT_WORKFLOW.md).

Deployment uses **two separate Vercel projects** connected to this repository:

- Frontend root: `frontend/`, framework: Next.js, standard build command.
- Backend root: `backend/`, framework: FastAPI, application: `app/main.py` exporting `app`.

Vercel supports this backend entrypoint without a custom routing configuration. See [Vercel FastAPI documentation](https://vercel.com/docs/frameworks/backend/fastapi). Configure each project's environment independently. Set the frontend API URL to the backend deployment URL and backend CORS to the exact frontend origin. Run reviewed migrations separately before enabling database-backed endpoints; application startup never applies schema changes. No Vercel projects, credentials, or production data resources are created by this foundation. See [DEPLOYMENT.md](DEPLOYMENT.md).

## Project contracts

- [AGENTS.md](AGENTS.md), [PRODUCT.md](PRODUCT.md), [ARCHITECTURE.md](ARCHITECTURE.md), [ROADMAP.md](ROADMAP.md)
- [DESIGN.md](DESIGN.md), [DESIGN_GUIDELINES.md](DESIGN_GUIDELINES.md)
- [DATABASE.md](DATABASE.md), [API.md](API.md), [IMPORTS.md](IMPORTS.md), [AI.md](AI.md), [DATA_AND_TELEMETRY.md](DATA_AND_TELEMETRY.md)
- [DEPLOYMENT.md](DEPLOYMENT.md), [GIT_WORKFLOW.md](GIT_WORKFLOW.md), [CODEX_PROMPTS.md](CODEX_PROMPTS.md), [CODEX_KICKOFF_PROMPT.md](CODEX_KICKOFF_PROMPT.md)

Continue only through separately authorized roadmap phases.
