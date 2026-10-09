# ARCHITECTURE.md

## Overview

CPA Study Hub uses a separated frontend/backend architecture.

```text
Browser
  |
  v
Next.js frontend
  |
  | HTTPS / REST
  v
FastAPI backend
  |
  +----------------------+----------------------+
  |                      |                      |
  v                      v                      v
Supabase PostgreSQL   Supabase Storage      AI provider
Supabase Auth
```

## Repository structure

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

## Frontend

Technology:

- Next.js
- React
- TypeScript
- Tailwind CSS
- shadcn/ui
- Lucide React
- Recharts when charts are actually implemented

Responsibilities:

- routing
- UI
- forms
- accessibility
- browser state
- API client
- auth session UI
- visualization

Proposed feature folders:

```text
frontend/src/features/
├── dashboard/
├── calendar/
├── subjects/
├── topics/
├── videos/
├── resources/
├── quizzes/
├── flashcards/
├── recall/
├── assessments/
├── analytics/
├── auth/
└── settings/
```

Frontend must not contain privileged Supabase keys or AI-provider secrets.

## Backend

Technology:

- Python
- FastAPI
- Pydantic
- SQLAlchemy and/or Supabase server SDK as finalized during the database phase

Proposed structure:

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

### API layer

Keep HTTP handlers thin:

- request parsing
- auth boundary
- validation handoff
- service calls
- response mapping

### Services

Business logic examples:

- schedule service
- progress service
- quiz service
- recall service
- resource service
- analytics service
- assessment service

### Repositories/data access

Use a consistent data-access boundary. Do not scatter SQL/Supabase queries through route handlers.

### Parsers

Planned:

```text
backend/app/parsers/
├── pdf_parser.py
├── csv_parser.py
├── quiz_csv_parser.py
├── flashcard_csv_parser.py
└── spreadsheet_importer.py
```

### AI

Planned:

```text
backend/app/ai/
├── client.py
├── quiz_generator.py
├── flashcard_generator.py
├── document_qa.py
├── summarizer.py
└── prompts/
```

AI provider calls stay server-side.

## Supabase

Supabase provides:

- PostgreSQL
- Auth
- Storage

FastAPI remains the primary application/business API.

The frontend may use documented browser-side Supabase Auth, but core application data operations should flow through FastAPI unless a later architecture decision explicitly documents an exception.

## Data-source strategy

Google Sheets/XLSX is an initial import source.

Production source of truth:

- PostgreSQL for structured data
- Supabase Storage for files

Do not model one production table per spreadsheet tab.

## API style

Initial style:

- REST
- JSON
- `/api/...`

Do not add versioning complexity until needed.

## Authentication

Supabase Auth is the identity provider.

FastAPI validates identity before privileged user-data operations.

Service-role credentials are backend-only.

### Implemented Phase 2 boundaries

The official Supabase JavaScript client lives in `frontend/src/features/auth/` and is used only for email/password sign-in, session persistence/refresh, and local-browser sign-out. `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` requires a current publishable key; backend configuration uses `SUPABASE_SECRET_KEY` for the current secret key. Legacy anon/service-role variables are not used by the application. The login route is `/login`; the existing shell at `/` uses a client session guard and waits for backend identity verification. No cookies or Next.js server auth APIs are introduced. The client guard is navigation behavior, never the security authority for data.

`frontend/src/services/api.ts` sends the current bearer access token to FastAPI. A reusable dependency in `backend/app/core/auth.py` validates it through Supabase Auth's `/auth/v1/user` endpoint using HTTPX and a backend-only API key. Only the verified UUID/email cross the auth boundary. Supabase outages fail closed with 503; invalid sessions return 401. No local unverified JWT decoding is used.

SQLAlchemy and Psycopg provide lazy server-side PostgreSQL access; Alembic owns version-controlled migrations under `backend/migrations/`. A subjects repository separates data access from HTTP handlers. No ORM abstractions are created for unused domains. Application startup never creates tables or runs migrations. `/health` can run with all Supabase settings blank.

Phase 2 introduced profiles, subjects, empty topics, Auth, `/api/auth/me`, and read-only `/api/subjects`. Profile creation uses a Supabase Auth trigger. Subsequent phases add curriculum imports, progress/planning and the Phase 7 resource boundary below. See DATABASE.md for the RLS and privileged-backend access model.

## Long-running work

### Phase 7 resource boundary

The Resource Library uses the existing verified bearer identity and SQLAlchemy
repository convention. FastAPI validates bounded multipart uploads, creates
owner-scoped metadata, delegates private object operations to an HTTPX Storage
service, and processes files through isolated PDF/CSV parsers. The browser never
creates resource metadata or supplies storage paths directly. The shared auth
layout and token recovery also serve multipart requests; no new auth provider exists.

Originals live in the private `study-resources` bucket. PostgreSQL stores resources
and ordered PDF page sections; CSV preview is read from the original, not a generic
permanent CSV-row table. Processing is synchronous and size/output bounded. Storage
upload precedes metadata creation and PDF extraction. The uploaded/processing
transitions and final ready/failed state commit together; intermediate states are
not durable background jobs. CSV validation occurs before Storage writes. Storage
and PostgreSQL cannot share a transaction: upload failures compensate new objects,
and deletion retains metadata when Storage fails. Provider/database failures are
reported without keys, signed links, file contents or raw exception text.

The resource processing service is the future worker boundary. No queue, OCR,
embeddings, document generation or AI calls are introduced by Phase 7.

Keep the first implementation simple.

If large PDF/AI processing later exceeds Vercel execution constraints, introduce a worker/job system as a separate architecture phase rather than rewriting the whole backend.

## Deployment

- frontend: Vercel project rooted at `frontend/`
- backend: Vercel project rooted at `backend/`
- database/auth/storage: Supabase

See `DEPLOYMENT.md`.

## Architectural invariants

Phase 9 adds private decks/cards/reviews through separate FastAPI schemas/routes/
repositories/services, reusing verified identity, curriculum checks and resources.
The pure versioned scheduling service calculates server-owned intervals/dates;
one transaction locks card revision, persists immutable history and advances current
state. No queue/worker, extra auth listener, new SDK or frontend scheduling authority.
Next.js reuses shared authenticated layout and renders editable authoring and
reveal/rating views. Workbook recall inspection is read-only and report-only.

Phase 8 keeps validation, source ownership, CSV normalization and scoring in
FastAPI, with separate quiz routes/schemas/repositories/services and a dedicated
CSV parser/import service. PostgreSQL stores questions/options, ordered quizzes,
private frozen attempt snapshots and persisted answers. Next.js owns authoring,
ordered selection, taking and review; it never computes authoritative scores.
The existing shared authenticated layout/client is reused without per-page guards
or extra listeners. CSV import uses existing backend signing credentials only;
no new secret, SDK, worker or paid resource is required.

1. Frontend and backend remain separately runnable.
2. Business logic stays backend-side.
3. Secrets stay server-side.
4. PostgreSQL is the structured-data source of truth.
5. Files live in managed object storage.
6. Imports are normalized before persistence.
7. AI-generated learning material retains source metadata where possible.
8. Schema/API changes are explicit and documented.
