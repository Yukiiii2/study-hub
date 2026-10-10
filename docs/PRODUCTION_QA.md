# Production readiness record

This record covers the final local readiness pass on 2026-10-10. It distinguishes
verified application behavior from pending browser and production acceptance.
No production hosting URL is known; no Vercel deployment was performed.

## Completed checks

| Area | Evidence / result |
| --- | --- |
| Backend regression checks | 206 focused tests across 15 existing domain/security modules passed. |
| Frontend regression checks | 12 existing render/session/API recovery/date/hierarchy/domain scripts and one temporary UI-handler check passed. They do not run a browser. |
| Production frontend build | `npm.cmd run build` passed compilation, TypeScript validation and route generation. |
| Local route availability | HTTP 200 for Dashboard, login, Subjects, Study Plan, Library, Question Bank, Quizzes/builder, Flashcards, Recall, Assessments, Focus, Analytics and Assistant. This checks route delivery, not browser authentication. |
| CORS / health | `/health` returned `ok`; bearer/content-type preflight accepted exact localhost origins on ports 3000/3001 and rejected an unapproved origin. |
| Supabase state | Migration revision `0010_ai_provenance`; seven subjects, 163 topics, 1,562 mapped videos and five imported owner-linked assessment definitions. No schema reset or production-data cleanup was performed. |
| Database / Storage security | All 24 application tables have RLS enabled; no anonymous table/column grants; no unexpected authenticated write grants or grading-key access. Resource bucket private, 4 MiB, owner-read policy and no browser mutation policies. |
| Dependency review | Full frontend `npm audit` reported zero vulnerabilities. Targeted OSV exact-version review of 13 direct/core Python packages found no advisories; this is not an exhaustive transitive Python audit. No dependency upgrades were made. |
| Secret/private-file hygiene | Real environment files and workbook remain ignored. Known backend credentials were absent from tracked files and public build assets; the staged artifact/credential scan passed. |
| Review | Independent review found no Critical or Important findings in source, deployment configuration and handoff documentation. |

## Live local domain checks

Existing explicit verification scripts use new synthetic Supabase users and
fixtures, real PostgreSQL/private Storage, and the local Study Hub API on 8001.
They do not mutate client-owned history.

| Verifier | Result |
| --- | --- |
| `scripts/verify_resources.py` | Passed PDF/CSV validation, bounded processing/preview, signed original access, deletion and owner/Storage/RLS isolation; cleanup passed. |
| `scripts/verify_study_planner.py` | Passed event/task/session CRUD, recurrence and owner/reference constraints; cleanup passed. |
| `scripts/verify_quizzes.py` | Passed bank/builder/attempt persistence, grading/concurrent submission, CSV confirmation/bounds and owner/RLS checks; cleanup passed. |
| `scripts/verify_flashcards.py` | Passed deck/card CRUD, due queue, ratings/history, retry/concurrency and isolation; cleanup passed. |
| `scripts/verify_assessments.py` | Passed coverage, manual results/history, readiness and archive/ownership checks; cleanup passed. |
| `scripts/verify_analytics_focus.py` | Passed authoritative start/finish, single-active-session/concurrent behavior, 7/30/90/custom periods, day splitting, planned/actual and ownership checks; cleanup passed. |
| `scripts/verify_ai_study.py` | Passed mocked-provider requests against real Auth/database: ownership, citations, bounded input/output, no implicit persistence, explicit signed saves, suspended cards, immutable grading and limits; cleanup passed. |

A temporary supplemental check also passed authenticated subject/topic details,
topic videos and Dashboard counts for all seven subjects. Start, complete,
repeat-complete and reset affected only the synthetic owner; another user's
progress stayed unchanged. Progress RLS and timestamp reset checks passed.

Final read-only cleanup found **zero matching verification Auth users and zero
profiles** across all eight fixture prefixes. Temporary helper scripts were
removed. Retained curriculum totals stayed at seven subjects/163 topics/1,562
videos, and the five imported assessment definitions remained intact.

The prior Phase 12 follow-up verified five bounded live Gemini calls, including
owned PDF Q&A/citations, quiz/card drafts and completed-answer explanation. This
pass uses the mocked-provider AI security/contract verifier rather than repeating
paid generation. Prior provider success is not proof of deployed operation.

## Focused usability fixes

- Compact navigation closes after a route change and focuses the new content.
- Login dependency failures offer a Retry connection action; provider errors stay
  sanitized and protected session behavior is preserved.
- Shared forms, selects, filters and modal headings resist intrinsic-width
  overflow; checkbox/file controls have 44-pixel targets.
- Heatmap text contrast is at least 4.5:1 across all five levels by calculation.
- Removed unavailable Settings filler and clarified user-facing implementation
  jargon. No core domain, scoring, scheduling or ownership behavior was changed.

## Pending acceptance / release blockers

No enabled automation browser was available; creating Chrome and in-app browser
surfaces failed. Source review and component tests cannot establish rendered
desktop/tablet/mobile layouts, zoom/touch behavior, native dialog focus trapping,
or complete browser sign-in/focus/navigation/sign-out behavior. Verify these with
an available browser before client acceptance.

No authenticated Vercel CLI, linked frontend/backend projects or accessible
hosting browser session was available. The owner must configure the two projects,
set production environment values, deploy, set the exact frontend CORS/Auth URLs,
and perform the production smoke checklist in [DEPLOYMENT.md](../DEPLOYMENT.md).
No production URLs, provider quota verification, backup automation or restore
drill are claimed. See [HANDOFF.md](HANDOFF.md) for responsibilities and actual
feature/source-data limitations.

Private workbooks, uploaded originals, environment values, temporary users and
temporary verification logs/helper scripts are not handoff artifacts. The pre-existing user change
to `frontend/next-env.d.ts` is preserved and excluded from the handoff commit.
