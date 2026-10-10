# Study Hub

Study Hub is a private CPALE study workspace for planning study, tracking lectures, managing resources, practising questions and flashcards, recording assessments, and reviewing actual study time. Its curriculum covers FAR, AFAR, MAS, TAX, RFBT, AT and AP.

The application consists of an independent **Next.js frontend** and **FastAPI backend**. Supabase provides Auth, PostgreSQL and private Storage; Gemini provides optional study assistance through the backend. Application data and business rules pass through FastAPI. The browser uses Supabase directly only for authentication.

Production: [study-hub-theta-ashy.vercel.app](https://study-hub-theta-ashy.vercel.app). One repository-root Vercel Services project serves Next.js pages and FastAPI `/api/*` on the same domain; production leaves `NEXT_PUBLIC_API_URL` unset.

## Implemented features

- Email/password sign-in, persistent sessions, protected pages and sign-out.
- Dashboard with today's plans, pending tasks, lecture summaries and recall counts; subjects, topics and private lecture progress.
- Month/week study planner, mobile agenda, recurring events, occurrence edits, tasks and recorded study sessions.
- Private PDF/CSV Resource Library, selectable-text PDF extraction, page references and expiring downloads.
- Question Bank, validated CSV question import, ordered quizzes, saved answers and server-graded attempt review.
- Private flashcard decks, editable cards, due recall and backend-owned spaced repetition; cards from quiz mistakes.
- Assessments with exact curriculum coverage, manual results/history and separate preparation indicators.
- Persistent Focus timer and analytics, including daily activity, planned versus actual time and session history.
- AI questions/summaries, quiz and flashcard drafts, and explanations of completed quiz answers. Drafts require explicit save; AI cards save suspended until separately activated.

See [handoff and limitations](docs/HANDOFF.md) for the exact supported scope and [production readiness record](docs/PRODUCTION_QA.md) for verified checks and pending acceptance. Product specifications also contain future requirements; they are not a claim that every listed feature is implemented.

## Technology and repository

Frontend: Next.js App Router, React, TypeScript, Tailwind CSS and the official Supabase JavaScript client. Backend: Python, FastAPI, Pydantic, HTTPX, SQLAlchemy, Psycopg, Alembic, pypdf and python-multipart. Local XLSX import tooling uses a separate optional requirements file.

```text
frontend/           Next.js pages, components, feature UI and authenticated API clients
backend/            FastAPI routes, services, repositories, parsers, AI and migrations
docs/               Handoff and detailed feature contracts
data/templates/     Supported import templates
data/imports/       Local ignored sources and reviewed safe reports
scripts/            Explicit verification utilities
```

Read [ARCHITECTURE.md](ARCHITECTURE.md) for service boundaries and [DEPLOYMENT.md](DEPLOYMENT.md) for the single-project Vercel Services workflow and live verification results.

## Prerequisites

- Node.js 20.9+ and npm; Python 3.13 (the validated and deployment-pinned runtime) and pip; Git.
- A configured Supabase project with PostgreSQL, Auth and Storage. Plain PostgreSQL alone lacks the Supabase Auth schema/roles required by migrations.
- Project-owner access for migrations, private bucket setup and confirmed account provisioning.
- Backend Gemini credentials and an explicit supported model identifier if AI is required.

## Windows local setup

Use **frontend port 3001** and **backend port 8001**. Port **8000 belongs to the separate F1 project and must remain untouched**. Run the apps in separate PowerShell terminals from the repository root. Copy example files only when creating a new environment; preserve existing configured files.

Frontend:

```powershell
cd frontend
Copy-Item .env.example .env.local
npm.cmd ci
# Configure .env.local before starting.
npm.cmd run dev -- --port 3001
```

Backend:

```powershell
cd backend
python -m venv .venv
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
# Configure .env before starting; apply reviewed migrations and bucket setup below.
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

Using `npm.cmd` avoids PowerShell script-policy problems. Calling the virtual environment's Python directly avoids activation. Open http://localhost:3001. The backend exposes http://localhost:8001/health and http://localhost:8001/docs. Health confirms process availability, not database, Storage or Gemini readiness.

For a local production frontend build, from `frontend/` use `npm.cmd run build` and `npm.cmd run start -- --port 3001`.

## Environment checklist

These are placeholders, not credentials. The frontend has exactly three public variables in ignored `frontend/.env.local`:

```dotenv
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_SUPABASE_URL=<supabase-project-url>
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=<current-sb_publishable-key>
```

The backend has exactly six application variables in ignored `backend/.env`:

```dotenv
SUPABASE_URL=<same-supabase-project-url>
SUPABASE_SECRET_KEY=<current-sb_secret-key>
DATABASE_URL=<postgresql-connection-url-with-TLS>
GEMINI_API_KEY=<backend-only-gemini-key>
GEMINI_MODEL=<explicit-supported-gemini-model-id>
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

Use current `sb_publishable_...` and `sb_secret_...` keys. The application does not use legacy anon/service-role variable names. Database and AI credentials stay backend-only. Obtain the connection URL from Supabase's Connect panel, URL-encode password characters and require TLS for hosted connections. Use a privileged direct or session-pooler connection for migrations; select an appropriate runtime connection as described in [DEPLOYMENT.md](DEPLOYMENT.md).

Backend settings load `backend/.env`; process environment takes precedence. Restart the backend after changes. Restart/rebuild the frontend after public environment changes. Production uses same-origin `/api/*` requests with `NEXT_PUBLIC_API_URL` unset. CORS can be empty for same-origin-only production or contain exact trusted origins, comma-separated; wildcards are rejected. The root `.env.example` is only a pointer and requires no root `.env`.

## Database, Storage and accounts

Review the migration chain against the intended Supabase project before applying it. From `backend/`:

```powershell
.\.venv\Scripts\python.exe -m alembic history
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m app.services.resource_storage
```

The current migration head is **`0010_ai_provenance`**. Migrations create the implemented domain tables, seed seven subjects and create/backfill Auth profiles. Startup never runs migrations. Curriculum/video/assessment imports are separate reviewed operations; a new database does not automatically contain the previously imported workbook data. Destructive downgrades are blocked. See [DATABASE.md](DATABASE.md) and [IMPORTS.md](IMPORTS.md).

Storage setup creates/verifies the private **`study-resources`** bucket with PDF/CSV MIME restrictions and a **4 MiB (4,194,304 bytes)** file limit. Incompatible or public buckets fail closed. Downloads use **120-second signed URLs**; treat them as temporary access credentials. Extracted PDF text is bounded and page-aware; OCR is deferred.

Enable Supabase email/password authentication. The project owner provisions accounts through Authentication > Users and ensures users are confirmed/enabled. The application provides sign-in only; it has no public sign-up or password-reset UI. Database profile timezone defaults to `Asia/Manila`.

## AI operation

Set both backend Gemini variables to enable AI. Missing configuration returns a sanitized unavailable response while ordinary study features remain independent. Requests use owned ready PDF passages, curriculum context or completed quiz snapshots. Passage summaries cover selected bounded context rather than every page of a large document.

Calls have prompt/context/output caps, a 30-second provider deadline, no automatic provider retries, and per-process rate/concurrency limits. Configure provider quota/billing controls before production; application limits reset on restart and do not coordinate across instances. AI cannot change deterministic scores, progress, recall history, schedules or permissions. See [AI.md](AI.md) and [handoff operating limits](docs/HANDOFF.md).

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Frontend cannot reach the API | `NEXT_PUBLIC_API_URL`, backend port 8001, and exact `CORS_ORIGINS`; confirm `/openapi.json` identifies Study Hub API. |
| Sign-in fails or pages return 401 | Same Supabase project on both apps, current key types, confirmed/enabled account and valid session. Sign out/in after a rejected session. |
| Database-backed pages return 503 | Correct database URL, TLS/network connectivity, reviewed migrations at `0010_ai_provenance`, and backend restart after environment changes. |
| Resource upload/download fails | Private bucket setup, PDF/CSV type, 4 MiB file cap and current short-lived download link. Scanned PDFs do not gain OCR text. |
| AI unavailable or request rejected | Both backend Gemini settings, model access/quota and supported owned context; reduce scope or retry later after a limit. Never expose raw provider errors or keys. |
| Subjects exist but topics/videos are empty | Migrations seed subjects only; review separate import/setup instructions rather than inventing sample curriculum or progress. |

Use [DEPLOYMENT.md](DEPLOYMENT.md) for publishing and production checks, and [docs/HANDOFF.md](docs/HANDOFF.md) for ownership, backups and known limitations. Development changes follow [AGENTS.md](AGENTS.md), [GIT_WORKFLOW.md](GIT_WORKFLOW.md) and the root product/design/API/database contracts.
