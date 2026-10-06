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

## Long-running work

Keep the first implementation simple.

If large PDF/AI processing later exceeds Vercel execution constraints, introduce a worker/job system as a separate architecture phase rather than rewriting the whole backend.

## Deployment

- frontend: Vercel project rooted at `frontend/`
- backend: Vercel project rooted at `backend/`
- database/auth/storage: Supabase

See `DEPLOYMENT.md`.

## Architectural invariants

1. Frontend and backend remain separately runnable.
2. Business logic stays backend-side.
3. Secrets stay server-side.
4. PostgreSQL is the structured-data source of truth.
5. Files live in managed object storage.
6. Imports are normalized before persistence.
7. AI-generated learning material retains source metadata where possible.
8. Schema/API changes are explicit and documented.
