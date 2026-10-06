# Study Hub

Study Hub is a focused study-management and learning workspace. Its current primary use case is CPALE review. The repository now implements **Phase 2 - Database and authentication foundation**. Live Supabase setup is required to enable sign-in and apply the schema.

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

Current stack: Next.js App Router, React, TypeScript, Tailwind CSS, and the official Supabase JavaScript client; Python, FastAPI, Pydantic, pydantic-settings, Uvicorn, HTTPX, SQLAlchemy, Alembic, and Psycopg. Supabase PostgreSQL and Auth are integrated through configuration; Storage and all study features remain deferred.

Frontend source is grouped into `src/app`, `src/components`, `src/features/auth`, `src/features/dashboard`, `src/lib`, `src/services`, and `src/styles`. Authentication helpers are separate from FastAPI clients. Backend code lives in `app/api`, `app/core`, `app/db`, `app/repositories`, `app/schemas`, and `app/main.py`; migrations live in `backend/migrations`. Additional folders will be added when actual features need them.

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
npm.cmd run dev
```

Open http://localhost:3000. For a production compile, use `npm.cmd run build`, then `npm.cmd start` to serve it locally.

`frontend/.env.local` is the frontend environment file:

```text
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=
```

Set `NEXT_PUBLIC_API_URL=http://localhost:8000` and configure the Supabase project URL and current publishable key (`sb_publishable_...`) in `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`. Legacy anon keys are not used. Only public values belong in this file; never put secret, database, or AI keys in frontend code or variables. Restart the dev server after changing environment values.

## Backend development

From the repository root, on Windows PowerShell:

```powershell
cd backend
python -m venv .venv
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Using the virtual environment's Python directly avoids requiring activation or a PowerShell policy change. Optional activation: `.\.venv\Scripts\Activate.ps1`.

On macOS/Linux:

```sh
cd backend
python3 -m venv .venv
source .venv/bin/activate
cp .env.example .env
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

`backend/.env` is loaded by centralized settings. Operating-system environment variables take precedence. Its example contains:

```text
SUPABASE_URL=
SUPABASE_SECRET_KEY=
DATABASE_URL=
GEMINI_API_KEY=
CORS_ORIGINS=
```

Configure `SUPABASE_URL`, `SUPABASE_SECRET_KEY`, and `DATABASE_URL` using the same Supabase project as the frontend. Leave `GEMINI_API_KEY` blank. Set `CORS_ORIGINS=http://localhost:3000` for local browser requests. Multiple explicit origins use a comma-separated list, for example `http://localhost:3000,http://127.0.0.1:3000`. An empty value allows no cross-origin browser access; wildcard origins are rejected. Current application endpoints use GET only.

Health endpoint: GET http://localhost:8000/health returns HTTP 200:

```json
{"status":"ok"}
```

Interactive API documentation is available at http://localhost:8000/docs. Health confirms the application is running, not database connectivity.

The root `.env.example` only points to application-specific files; no root environment file is needed. All real environment files, virtual environments, dependencies, and build outputs are Git-ignored. Example files are tracked.

## Supabase setup and migrations

Use an existing hosted Supabase project or your own separately configured local Supabase instance. A plain PostgreSQL database alone is insufficient: the migrations require Supabase's `auth.users`, `auth.uid()`, and `anon`/`authenticated` roles. No external project is created automatically.

Obtain the project URL and current publishable key from Supabase project settings. Obtain the backend-only current secret key (`sb_secret_...`) and PostgreSQL connection string separately. Use the Connect panel's direct or session-pooler connection for migrations; the session pooler is useful on IPv4 networks. `DATABASE_URL` accepts `postgresql://...` or `postgresql+psycopg://...`. Copy the actual connection details, URL-encode special characters in the database password, and require TLS for hosted connections with `?sslmode=require`. Use the Connect panel's transaction-pooler URL for a serverless backend if appropriate; the driver disables prepared statements and application pooling. Never put credentials in examples or terminal output; real values belong only in the two Git-ignored application environment files.

From `backend/`, after setting `backend/.env`:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic current
```

`upgrade head` applies the structural migration and the seed migration. It creates only `profiles`, `subjects`, and `topics` (plus Alembic's version table). The seed inserts FAR, AFAR, MAS, TAX, RFBT, AT, and AP with stable UUIDs and order 1-7. Re-running upgrades does not duplicate data. No separate seed command or sample topics are required. Migrations are hand-authored; create the next reviewed migration with `python -m alembic revision -m "description"`. Automatic ORM schema generation is not used. Destructive downgrades deliberately fail.

Without credentials, inspect the migration chain and generated SQL:

```powershell
.\.venv\Scripts\python.exe -m alembic history
.\.venv\Scripts\python.exe -m alembic upgrade head --sql
```

Offline generation does not apply or prove the SQL against a live database. See [DATABASE.md](DATABASE.md) for constraints and RLS. A database trigger creates one profile per Auth user and backfills existing users; the default timezone is `Asia/Manila`.

## Authentication flow

Enable email/password authentication in Supabase. Create a test account through the Supabase Dashboard's Authentication > Users interface and ensure it is confirmed/enabled. This phase provides sign-in only; there is no sign-up or password-reset UI.

Open `/login`, sign in, and return to `/`. The official SDK persists and refreshes the browser session. The protected Dashboard waits for FastAPI to verify the access token before rendering the shell. Unauthenticated sessions redirect to `/login`; sign-out ends this browser's session. Session persistence uses browser local storage, not server cookies, so the Next.js page guard is a client guard. Every protected FastAPI endpoint independently enforces authentication; do not use the client guard as authorization for future server-side data.

`src/services/api.ts` obtains the current session and sends `Authorization: Bearer <access_token>` to FastAPI. It never queries application tables through the browser SDK. FastAPI validates each token with Supabase's `/auth/v1/user` endpoint; `/api/auth/me` returns only the verified UUID and email. `/api/subjects` reads the database through the backend repository. Missing/invalid sessions return 401, while unavailable/unconfigured services return sanitized 503 errors. `/health` remains public and independently runnable without Supabase credentials.

The Dashboard includes a small authenticated-user indicator and a **Check subject setup** button, which reads the protected subject definitions and displays the actual returned count. This verifies the browser-to-FastAPI-to-database path without building subject management.

Narrow backend checks (mocked Supabase and database boundaries):

```powershell
cd backend
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_auth_foundation.py -v
```

Live verification after setup: sign in, reload to check session persistence, check subject setup (seven on a fresh migration), sign out, and confirm `/` redirects to `/login`. Confirm protected endpoints return 401 without a bearer token. Never paste real tokens into tracked files.

## Current scope and deferrals

The Phase 1 dark shell and placeholder remain intact, with minimal authentication added. Planned navigation is unavailable. RLS permits own-profile reads/updates and authenticated curriculum reads, with no normal-user curriculum writes. Direct backend database credentials can bypass RLS: verified identity and explicit user scoping are mandatory for future user-owned repositories.

Intentionally deferred: actual subject/topic management UI, topic data, videos, spreadsheet migration, calendar/planner, tasks/sessions, resources/uploads, Storage, PDF/CSV processing, quizzes, flashcards/recall, assessments, analytics, and AI. There are no fake study metrics or charts.

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
