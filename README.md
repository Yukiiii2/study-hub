# Study Hub

Study Hub is a focused study-management and learning workspace. Its current primary use case is CPALE review. This repository implements **Phase 1 - Repository Foundation** only.

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

Current stack: Next.js App Router, React, TypeScript, Tailwind CSS; Python, FastAPI, Pydantic, pydantic-settings, and Uvicorn. Supabase PostgreSQL/Auth/Storage are planned for later phases and are not connected. No future-feature SDKs are installed.

Frontend source is grouped into `src/app`, `src/components`, `src/features/dashboard`, `src/lib`, `src/services`, and `src/styles`. The health client is available for future use but is not called by the placeholder UI. Backend code lives in `app/api`, `app/core`, and `app/main.py`. Additional folders will be added when actual features need them.

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
NEXT_PUBLIC_SUPABASE_ANON_KEY=
```

Set `NEXT_PUBLIC_API_URL=http://localhost:8000` when calling the local backend. Supabase variables remain blank in Phase 1. Only public values belong in this file; never put service-role or AI keys in frontend code or variables.

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
SUPABASE_SERVICE_ROLE_KEY=
DATABASE_URL=
GEMINI_API_KEY=
CORS_ORIGINS=
```

Leave future-service variables blank. Set `CORS_ORIGINS=http://localhost:3000` for local browser requests. Multiple explicit origins use a comma-separated list, for example `http://localhost:3000,http://127.0.0.1:3000`. An empty value allows no cross-origin browser access; wildcard origins are rejected. Phase 1 allows GET requests only. Expand methods alongside future API implementation.

Health endpoint: GET http://localhost:8000/health returns HTTP 200:

```json
{"status":"ok"}
```

Interactive API documentation is available at http://localhost:8000/docs. Health confirms the application is running, not database connectivity.

The root `.env.example` only points to application-specific files; no root environment file is needed. All real environment files, virtual environments, dependencies, and build outputs are Git-ignored. Example files are tracked.

## Phase 1 scope

The frontend contains a dark responsive shell, desktop sidebar, compact expandable mobile navigation, and Dashboard placeholder. Planned navigation labels are unavailable rather than linking to unimplemented pages. The backend contains configuration, environment-driven CORS, and health only.

Intentionally deferred: database schema/migrations, authentication, subjects/topics, videos, spreadsheet migration, calendar/planner, tasks/sessions, resources/uploads, PDF/CSV processing, quizzes, flashcards/recall, assessments, analytics, and AI. There are no fake study metrics or charts.

## Git and deployment

Repository: https://github.com/Yukiii2/study-hub.git. Early solo work uses `main`, with one focused commit per completed phase. Review diffs and secrets before staging; never commit real `.env` files or rewrite remote history. See [GIT_WORKFLOW.md](GIT_WORKFLOW.md).

Deployment uses **two separate Vercel projects** connected to this repository:

- Frontend root: `frontend/`, framework: Next.js, standard build command.
- Backend root: `backend/`, framework: FastAPI, application: `app/main.py` exporting `app`.

Vercel supports this backend entrypoint without a custom routing configuration. See [Vercel FastAPI documentation](https://vercel.com/docs/frameworks/backend/fastapi). Configure each project's environment independently. Set the frontend API URL to the backend deployment URL and backend CORS to the exact frontend origin. No Vercel projects, credentials, or production data resources are created by this foundation. See [DEPLOYMENT.md](DEPLOYMENT.md).

## Project contracts

- [AGENTS.md](AGENTS.md), [PRODUCT.md](PRODUCT.md), [ARCHITECTURE.md](ARCHITECTURE.md), [ROADMAP.md](ROADMAP.md)
- [DESIGN.md](DESIGN.md), [DESIGN_GUIDELINES.md](DESIGN_GUIDELINES.md)
- [DATABASE.md](DATABASE.md), [API.md](API.md), [IMPORTS.md](IMPORTS.md), [AI.md](AI.md), [DATA_AND_TELEMETRY.md](DATA_AND_TELEMETRY.md)
- [DEPLOYMENT.md](DEPLOYMENT.md), [GIT_WORKFLOW.md](GIT_WORKFLOW.md), [CODEX_PROMPTS.md](CODEX_PROMPTS.md), [CODEX_KICKOFF_PROMPT.md](CODEX_KICKOFF_PROMPT.md)

Continue only through separately authorized roadmap phases.
