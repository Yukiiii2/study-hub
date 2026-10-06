# GIT_WORKFLOW.md

## Purpose

Keep Codex work reviewable and push only completed phase work.

## Repository

One repository contains independent `frontend/` and `backend/` applications plus shared project documentation.

## Branch strategy

For early solo development, direct `main` work is acceptable if that is the user's workflow.

If feature branches are useful, use short names such as:

- `foundation/backend`
- `feature/calendar`
- `feature/quiz-engine`

Do not add branch complexity without a reason.

## Commit discipline

Before committing:

1. inspect `git status`
2. inspect the relevant diff
3. confirm no secrets
4. stage only files belonging to the completed task
5. avoid unrelated generated files

Suggested messages:

```text
chore: initialize frontend and backend structure
feat: add study event API
feat: add subject progress dashboard
docs: define quiz import format
fix: correct calendar event validation
```

## Never commit

- `.env`
- `.env.local`
- service-role keys
- AI API keys
- database passwords
- build output
- virtual environments
- dependency caches
- editor/system junk

## Push rules

When a prompt explicitly authorizes push:

- push only after requested work is complete
- push only the intended branch
- never force push
- never rewrite history
- never guess a remote URL

If no remote exists, report that a remote must be configured.

If authentication fails, report the blocker and stop.

## Completion report

When commit/push is authorized, include:

- commit hash if available
- commit message
- branch
- push result
- intentionally uncommitted files

## Deployment vs push

Git push and Vercel deployment are separate actions.

A phase may authorize:

- commit only
- commit + push
- commit + push + deploy

Follow the exact prompt.

## No destructive Git operations

Never run without explicit approval:

- `git reset --hard`
- `git clean -fd`
- force push
- destructive history rewrite
- branch/tag deletion
