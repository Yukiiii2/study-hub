# Codex Kickoff Prompt — Phase 1 Repository Foundation

You are starting a new project named **CPA Study Hub**.

I have attached the project Markdown specification files. Read all of them before making changes:

- `AGENTS.md`
- `PRODUCT.md`
- `DESIGN.md`
- `DESIGN_GUIDELINES.md`
- `ARCHITECTURE.md`
- `DATABASE.md`
- `API.md`
- `IMPORTS.md`
- `AI.md`
- `DATA_AND_TELEMETRY.md`
- `DEPLOYMENT.md`
- `GIT_WORKFLOW.md`
- `ROADMAP.md`
- `README.md`
- `CODEX_PROMPTS.md`

Treat those files as project contracts. If they conflict with this prompt, this prompt controls only for the explicit Phase 1 scope below. Do not silently rewrite the contracts.

## Goal

Implement **Phase 1 — Repository Foundation only**.

This is scaffolding/foundation. Do not build product features yet.

## Required repository structure

Keep frontend and backend as separate applications inside one repository:

```text
cpa-study-hub/
├── frontend/
├── backend/
├── docs/
├── data/
│   ├── imports/
│   ├── templates/
│   └── seed/
├── scripts/
├── AGENTS.md
├── README.md
├── .gitignore
└── .env.example
```

If the attached Markdown files are currently at repository root, keep `AGENTS.md` and `README.md` at root. Move the other specification files into `docs/` only if you can update all references consistently and without unnecessary duplication. Prefer the simplest clean layout.

## Frontend foundation

Create `frontend/` using:

- Next.js
- React
- TypeScript
- Tailwind CSS

Use a current stable setup compatible with Vercel.

Add shadcn/ui only if setup is straightforward and does not require feature implementation.

Add Lucide React only if needed for the base shell.

Do not add Recharts until a real chart feature needs it unless it is already part of the selected starter.

Create only a minimal shell proving the design direction:

- dark-first
- left navigation on desktop
- responsive navigation behavior
- main content area
- simple placeholder Dashboard page
- no fake metrics
- no fake charts
- no invented CPA progress data

The shell must follow `DESIGN.md` and `DESIGN_GUIDELINES.md`.

Do not implement:

- subject pages
- calendar
- quizzes
- flashcards
- resource upload
- analytics
- AI

Create a frontend API-client/config location suitable for later FastAPI calls. Do not invent feature endpoints beyond the documented health route if you choose to wire a health check.

Create `frontend/.env.example`:

```text
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
```

Do not create or commit real secrets.

## Backend foundation

Create `backend/` using:

- Python
- FastAPI
- Pydantic

Use a clean structure aligned with `ARCHITECTURE.md`, for example:

```text
backend/app/
├── api/
├── core/
├── db/
├── models/
├── schemas/
├── repositories/
├── services/
├── integrations/
├── parsers/
├── ai/
└── main.py
```

Do not fill architectural folders with unnecessary abstractions. Add package markers only where needed.

Implement:

- FastAPI application
- centralized settings/config
- CORS from environment
- `GET /health`
- clear local run instructions

Health response:

```json
{
  "status": "ok"
}
```

Do not connect to Supabase yet unless a trivial placeholder/config boundary is needed. Database/auth implementation belongs to Phase 2.

Create `backend/.env.example`:

```text
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
DATABASE_URL=
GEMINI_API_KEY=
CORS_ORIGINS=
```

No real credentials.

## Root setup

Create/update:

- root `.gitignore`
- root `.env.example` only if it adds useful cross-project documentation without duplicating secret values
- `data/imports/`
- `data/templates/`
- `data/seed/`
- `scripts/`

Use `.gitkeep` only when useful.

Update `README.md` so a developer can understand:

- product purpose
- frontend/backend separation
- prerequisites
- frontend install/run
- Python virtual environment
- backend install/run
- environment-file locations
- health endpoint
- current phase/status
- intentionally deferred features

## Dependency discipline

Only install dependencies required for Phase 1.

Do not add future-phase dependencies such as:

- PDF parsing libraries
- CSV libraries unless starter tooling requires one
- Supabase SDK
- SQLAlchemy
- Gemini/OpenAI SDK
- Recharts

unless Phase 1 genuinely needs them.

## Validation authorized for this phase

You may perform only narrow foundation validation needed to confirm scaffolding is usable.

Allowed:

- install required dependencies
- verify project creation
- narrow frontend startup/compile validation if needed
- Python import/syntax validation
- verify FastAPI `/health` locally if straightforward

Do not run broad test suites, browser automation, or unrelated diagnostics.

Do not fix unrelated global-machine warnings.

## Git and push authorization

For this Phase 1 task, I explicitly authorize:

- `git status`
- review of the Phase 1 diff
- staging only Phase 1 files
- one focused commit
- pushing the current branch to the already-configured remote

Use a commit message similar to:

`chore: initialize CPA Study Hub foundation`

Do not force push.
Do not rewrite history.
Do not create or guess a remote URL.
Do not commit secrets.

If no remote is configured or authentication fails, finish the project files first, then report the exact blocker instead of attempting risky alternatives.

## Deployment / publish authorization

If this repository already has authenticated Vercel configuration and deploying the placeholder foundation is straightforward, you may deploy the frontend and backend as **separate Vercel projects** using roots:

- `frontend/`
- `backend/`

However:

- do not invent Vercel project names
- do not invent credentials
- do not create production Supabase resources during Phase 1
- do not block foundation work on deployment
- if deployment needs user setup, stop after preparing deployable code and report the exact next step

A successful Git push is more important than deployment during Phase 1.

## Scope protection

Do not implement future roadmap phases.

Specifically do not build:

- database migrations/schema
- Supabase Auth integration
- subject CRUD
- spreadsheet import
- calendar
- resources
- PDF/CSV processing
- quizzes
- flashcards
- assessments
- analytics
- AI

The goal is a clean, deployable foundation only.

## Completion report

When complete, report concisely:

1. repository structure created
2. frontend foundation
3. backend foundation
4. environment-example files
5. validation actually performed
6. files/features intentionally deferred
7. Git commit hash/message if committed
8. push result
9. deployment result or exact blocker if not deployed

Do not continue into Phase 2.
