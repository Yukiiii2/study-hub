# DEPLOYMENT.md

## Target deployment

### Frontend

- platform: Vercel
- framework: Next.js
- project root: `frontend/`

### Backend

- platform: Vercel
- framework: FastAPI
- project root: `backend/`

### Data services

- Supabase PostgreSQL
- Supabase Auth
- Supabase Storage

## Topology

```text
Vercel frontend
  |
  | HTTPS
  v
Vercel FastAPI backend
  |
  +--> Supabase PostgreSQL
  +--> Supabase Storage
  +--> AI provider
```

## Environment variables

### Frontend

```text
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
```

Only truly public variables may use `NEXT_PUBLIC_`.

### Backend

```text
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
DATABASE_URL=
GEMINI_API_KEY=
CORS_ORIGINS=
```

Never expose backend secrets to frontend code.

## Local environment files

Expected:

```text
frontend/.env.local
backend/.env
```

They must be Git-ignored.

Provide `.env.example` files with placeholder names only.

## Vercel project separation

Recommended:

- one Vercel project rooted at `frontend/`
- one Vercel project rooted at `backend/`

This keeps builds, logs, variables, and deployments independent.

## Backend considerations

FastAPI is acceptable for the initial API on Vercel.

Potential future limits:

- large PDF processing
- long AI generation
- heavy background jobs

If those become real limitations, move only long-running processing to a worker/service instead of rewriting the main backend.

## CORS

Allow local frontend origin during development.

Production should allow only required deployed frontend origins.

Avoid unrestricted wildcard CORS with authenticated production requests unless explicitly justified.

## Storage

Store uploaded files in Supabase Storage. Store metadata/reference in PostgreSQL.

Do not store large PDF binary blobs in normal relational columns.

## Initial production workflow

1. Push repository.
2. Create/configure Supabase project.
3. Apply migrations.
4. Configure backend Vercel project.
5. Set backend environment variables.
6. Deploy backend.
7. Configure frontend Vercel project.
8. Set frontend variables including API URL.
9. Deploy frontend.
10. Update backend CORS as needed.
11. Manually verify health/auth/basic API.

## Deployment authorization

Do not deploy automatically during ordinary feature work.

A Codex phase may explicitly authorize deployment.

If authorized:

- do not invent credentials
- use existing authenticated configuration only
- do not destructively alter production data
- report the result
- if setup is missing, stop and state the exact required user action

## Production safety

Never drop/reset production tables or delete production storage without explicit approval.
