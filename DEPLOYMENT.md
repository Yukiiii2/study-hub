# DEPLOYMENT.md

## Phase 12 AI configuration

Set GEMINI_API_KEY and GEMINI_MODEL only in backend runtime configuration
(locally backend/.env). Examples remain blank. Choose an accessible Gemini text
model supporting structured JSON from the
[provider catalog](https://ai.google.dev/gemini-api/docs/models). Never expose an
AI key through NEXT_PUBLIC variables. Apply additive 0010_ai_provenance first.
Missing provider settings return sanitized 503 while existing features work.
Configure provider/project quotas as the external hard cost boundary; in-process
limits reset and do not coordinate multiple workers. Selected passages leave
Study Hub only after an authenticated user explicitly requests AI assistance.
No paid provider project or deployment is provisioned. Generation has a 30-second
deadline/no retries; workers and distributed quotas remain separate future work.

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
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=
```

Only truly public variables may use `NEXT_PUBLIC_`.

### Backend

```text
SUPABASE_URL=
SUPABASE_SECRET_KEY=
DATABASE_URL=
GEMINI_API_KEY=
CORS_ORIGINS=
```

Never expose backend secrets to frontend code.

## Local environment files

### Phase 2 Supabase preparation

Use a configured Supabase project (hosted or an independently managed local Supabase instance). This phase does not create external resources. Obtain the project URL, publishable key, backend secret key, and PostgreSQL connection string from that project. Configure email/password Auth and create a confirmed test user through Authentication > Users; the application has no sign-up UI.

Use `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` for the current publishable key and `SUPABASE_SECRET_KEY` for the current secret key. Legacy anon/service-role environment variables are not used. Never put a secret key or database URL in any public variable. The backend sends the secret key only as the Auth verification API's `apikey` header; the user's access token remains the bearer token. SQLAlchemy uses `DATABASE_URL` for database access. AI variables stay blank. Real local credentials belong only in the Git-ignored `frontend/.env.local` and `backend/.env` files.

Set `DATABASE_URL` using the Connect panel's direct or session-pooler connection for migrations, with URL-encoded password characters and TLS (`sslmode=require`) for hosted Supabase. Use the transaction pooler for a serverless runtime when appropriate. The backend uses Psycopg with prepared statements disabled and SQLAlchemy NullPool; Supabase handles pooling. Never copy example project IDs or invent connection credentials.

Apply reviewed migrations from `backend/` with the virtual environment's `python -m alembic upgrade head`. This also seeds the seven CPA subjects and creates/backfills profiles. Use a privileged migration connection with access to the Auth schema and role grants. Runtime startup does not migrate; migration failure must be resolved before enabling database-backed endpoints. This is an initial additive schema migration, not a reset. Downgrade commands that would drop foundation data are blocked.

Configure the frontend API URL and Supabase public values, and the backend Supabase/database values and exact CORS origins independently in their Vercel projects. Redeploy the frontend after public environment changes. Validate sign-in, reload/session persistence, `/api/auth/me`, subject browsing, and sign-out after migrations. Phase 2 Auth checks do not require Storage; Phase 7 Library setup is documented below. AI configuration remains deferred.

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

### Phase 7 setup

Apply reviewed revision `0005_resources` using the configured migration connection.
Then, from `backend/`, run `python -m app.services.resource_storage` to create or verify the
private `study-resources` bucket. Existing incompatible/public bucket configuration
must fail closed; do not silently make uploaded files public. Storage policies are
version-controlled in the migration: owner-path plus matching own metadata SELECT,
no browser mutation policies. The backend uses the existing SUPABASE_URL and
SUPABASE_SECRET_KEY with HTTPX; no frontend secret or new credentials are needed.

Use current keys in the apikey header; a secret key is not a bearer JWT. Normal
resource requests still authenticate using the user's Supabase bearer token.
Download links expire after 120 seconds and must not be logged or persisted by
the browser. A recipient holding a signed link can use it until expiry; deletion
of the underlying object removes availability.

Uploads are limited to 4 MiB (4,194,304 bytes), below Vercel's 4.5 MB request-body
ceiling with room for multipart fields. The API separately bounds the multipart
envelope. This intentionally supports smaller documents than a 25/50 MB local
limit that would fail on the target runtime. See [Vercel limits](https://vercel.com/docs/functions/limitations).
PDF extracted output and content responses must also remain bounded; content is
paginated. Synchronous parsing stays in an isolated service; large/long-running
documents require a separately approved worker/upload architecture later.

No deployment is performed by Phase 7. If bucket creation or policy migration
permissions are unavailable, configure this private bucket and apply the reviewed
policies with project-admin access; do not broaden security to bypass the blocker.

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
