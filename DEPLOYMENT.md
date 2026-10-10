# Deployment

Study Hub uses two independent Vercel projects from the same repository and the
existing Supabase project. Deployment does not run database migrations or import
the personal workbook. No production URLs are recorded until deployments exist.

## Environment checklist

Set these in the **frontend** Vercel project for the intended environment:

| Variable | Value to configure |
| --- | --- |
| `NEXT_PUBLIC_API_URL` | Actual HTTPS backend deployment origin, without `/api` |
| `NEXT_PUBLIC_SUPABASE_URL` | Existing Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` | Current publishable key from that project |

Set these only in the **backend** Vercel project:

| Variable | Value to configure |
| --- | --- |
| `SUPABASE_URL` | Same existing Supabase project URL |
| `SUPABASE_SECRET_KEY` | Current backend secret key |
| `DATABASE_URL` | TLS-enabled PostgreSQL connection string; URL-encode password characters |
| `CORS_ORIGINS` | Comma-separated exact permitted frontend origins |
| `GEMINI_API_KEY` | Existing Gemini provider key |
| `GEMINI_MODEL` | Explicit accessible Gemini model supporting structured JSON output |

Do not substitute legacy anon/service-role variables. A current Supabase secret
key is an `apikey`, not a bearer JWT. Requests to Study Hub still carry the
authenticated user's bearer token. Never put backend variables in `NEXT_PUBLIC_*`.
Changing public Next.js variables requires a new frontend build/deployment.

Local values belong only in Git-ignored `frontend/.env.local` and `backend/.env`.
Keep `.env.example` files blank. Local configuration is independent of production:

```dotenv
# frontend/.env.local (public local API origin only)
NEXT_PUBLIC_API_URL=http://localhost:8001

# backend/.env (local origins only)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

`CORS_ORIGINS` is split on commas and whitespace is trimmed. Wildcards are
rejected. Production should list only the required deployed frontend origin(s),
not localhost or every Vercel preview. CORS does not replace authentication.

## 1. Verify existing Supabase services

1. Confirm the backend and frontend refer to the same existing project. Do not
   create or reset a project as part of deployment.
2. Review and apply pending additive migrations from `backend/`, using a
   privileged migration connection with the required Auth/Storage schema access:

   ```powershell
   .\.venv\Scripts\python.exe -m alembic current
   .\.venv\Scripts\python.exe -m alembic upgrade head
   .\.venv\Scripts\python.exe -m alembic current
   ```

   Current application head is `0010_ai_provenance`. Review future migrations
   before applying them; never reset, downgrade or truncate production data.
   Startup does not migrate automatically.
3. Use the Connect panel's direct/session-pooler URL for migrations. A compatible
   transaction-pooler URL is suitable for the serverless runtime. Include TLS
   (`sslmode=require`) for hosted Supabase. SQLAlchemy uses `NullPool`; Psycopg
   prepared statements are disabled for pooler compatibility.
4. Confirm Auth email/password sign-in and the intended client account. There is
   no public sign-up UI; account provisioning is an owner responsibility. After
   frontend deployment, set Supabase Auth Site URL and any required redirect
   allowlist to actual approved frontend URLs.
5. Verify the private resource bucket from `backend/`:

   ```powershell
   .\.venv\Scripts\python.exe -m app.services.resource_storage
   ```

   This creates/verifies `study-resources` and rejects incompatible/public bucket
   configuration. Reviewed migrations define owner-path plus matching resource
   metadata read policies, with no browser mutation policies. Do not broaden
   policies to work around a permissions failure.

## 2. Deploy backend

Use the owner's authenticated Vercel account and an existing authorized project,
or have the owner create/configure the project. Import the existing Git repository
and set **Root Directory: `backend`**, **Framework: FastAPI**. Configure the six
backend variables above. Choose project/team names through the owner's account;
this repository does not prescribe or fabricate them.

Vercel detects the existing `app/main.py` top-level FastAPI `app` and installs
`requirements.txt`. No catch-all adapter or route rewrite is required. Python
3.13 is pinned in `.python-version` to match the validated local runtime. See
[Vercel FastAPI support](https://vercel.com/docs/frameworks/backend/fastapi) and
[Python runtime configuration](https://vercel.com/docs/functions/runtimes/python).

Record the actual stable backend production URL and verify `GET /health` returns
`{"status":"ok"}`. Deployment protection must permit normal requests from the
intended frontend; interactive Vercel login protection on the API origin will
block browser calls. Keep Study Hub bearer authentication enabled. Preview
deployments need separately approved environment/origin/protection configuration;
do not send previews to production data by default.

Local Uvicorn remains unchanged:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8001
```

Port 8000 belongs to a separate local project.

## 3. Deploy frontend

Configure a separate project from the same repository with **Root Directory:
`frontend`**, **Framework: Next.js**. Use the package lockfile and standard build:
`npm ci`, then `npm run build`. Set all three public variables, using the actual
backend production URL. Deploy and record the actual stable frontend URL.

Separate root directories keep deployment variables, builds and logs independent.
See [Vercel monorepo project setup](https://vercel.com/docs/monorepos).

## 4. Complete production CORS and smoke checks

Set backend production `CORS_ORIGINS` to the exact deployed frontend origin and
redeploy the backend. Update Supabase Auth URLs as described above. Verify from
the deployed frontend, not just a local terminal:

- Sign in, reload/session restore, internal navigation, sign out, and logged-out
  access denial.
- Authenticated `/api/auth/me`, Dashboard and Subjects/Topics/Videos.
- Planner events/tasks/recurrence/sessions; Library upload, content, download and
  deletion; Question Bank/quiz attempt/save/submit/review.
- Flashcards/Recall; Assessments; Focus reload/finish; Analytics periods/history.
- Assistant resource Q&A/citations, quiz/card drafts and explicit save, and quiz
  explanations. Never test with another user's resources.
- Desktop, tablet and mobile layout, keyboard focus and dialogs.

Use temporary synthetic fixtures and remove their files, records and accounts.
Do not test by deleting client data. Check OPTIONS preflight allows the exact
frontend origin and required bearer/content-type headers; reject other origins.
Record remaining acceptance checks in [the handoff](docs/HANDOFF.md).

## Runtime boundaries and maintenance

Uploads accept PDF/CSV only, at most **4 MiB** of file content with a separately
bounded multipart envelope. Resource content is paginated. This stays below
Vercel's **4.5 MB request/response ceiling**; see
[function limits](https://vercel.com/docs/functions/limitations). Preserve these
bounds rather than increasing a local upload limit that cannot deploy reliably.
Signed resource URLs expire after 120 seconds; treat them as temporary bearer
access and do not log or persist them.

PDF extraction is synchronous, bounded and isolated in a service. OCR and a
background worker are not implemented. Large/long-running jobs require a
separately approved worker/upload architecture, not an adapter rewrite.

AI settings stay server-side. Missing configuration returns a sanitized 503
without disabling the other domains. AI generation has a 30-second deadline and
no automatic retries. Set Gemini project quotas/budgets as the external cost
boundary: in-process rate limits do not coordinate multiple serverless instances.
Selected document passages leave Study Hub only on an explicit authenticated AI
request. See [AI.md](AI.md) for limits and saving rules.

Review production logs without recording keys, passwords, bearer tokens, signed
URLs or private document contents. Maintain separate database and Storage-file
backups; database backups alone do not preserve Storage originals. Keep account,
billing, recovery, backup and provider-quota ownership with the client. See
[docs/HANDOFF.md](docs/HANDOFF.md) for maintenance and limitations.

## Current deployment status

Production deployment has not been performed in this readiness pass: no Vercel
CLI authentication, linked projects or accessible browser session were available.
No production frontend/backend URLs are known. The owner must configure the two
projects and their environment variables, then run the production smoke checks.
Local verification is not a substitute for production/browser acceptance.
