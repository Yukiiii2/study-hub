# Global loading state audit

## Shared rules

- `ContentSkeleton` provides static neutral-slate rows, detail, chart, calendar, dashboard and control-sized placeholders. Decorative shapes are hidden from assistive technology; visible status text and `aria-busy` describe pending reads. Skeletons have no pulse animation.
- `LoadNotice` distinguishes an unknown initial result from retained data. Initial reads use a local skeleton; subsequent reads use a compact refresh notice. Failures offer retry and identify retained data.
- The protected route `loading.tsx` sits below the existing shared layout. Auth/session infrastructure is unchanged: only genuine initial bootstrap blocks; validated sessions retain the shell during refresh and transient failures.
- Preserve abort handling, identity checks, explicit mutation confirmation, quiz draft recovery, recall request identities and existing server-owned calculations.
- Mutation guards synchronously reject rapid duplicate submissions. Related form fields/actions remain disabled while their transaction is pending; unrelated navigation and page content remain available.

## Surface audit

| Area | Result |
| --- | --- |
| Dashboard | Dashboard-shaped initial skeleton; loaded docket and all existing sections retained during retry/failure. Refresh is scoped to its control. |
| Study Plan | Separate context/task/event readiness; successful sections appear independently. Retains the loaded period during month/week/date fetches, labels its dates, and swaps only after success. Unknown event/task data never becomes a zero/empty state. |
| Focus | Detail skeleton only before its first snapshot. Background status keeps the running timer/context/totals visible. Existing start/finish guards and server duration logic preserved. |
| Subjects | Retries retain the directory. |
| Subject detail | Same-subject curriculum/lecture snapshots retained; pending lecture summary is localized. Different subject identities do not reuse another subject's presentation. |
| Lectures | Retains rows/progress during read retry; progress mutation serialization/recovery remains intact. |
| Recall | Initial queue skeleton, compact refresh, existing pending-review recovery and rating protection retained. |
| Flashcards/decks/history | Independent localized reads, retained lists, guarded saves and existing per-card history/recovery behavior. |
| Quizzes/Question Bank | Retained lists and history; local attempt/editor skeletons. Save/start/resume/import/submit labels describe their operation. Existing answer protection and persisted drafts unchanged. |
| Assessments | Retains definitions, coverage and result history during refresh or independent failure. Existing ownership, validation and scoring unchanged. |
| Library/resource detail | List, metadata and preview skeletons are independent. Loaded previews/metadata survive retries. Download/delete are guarded and retain their existing confirmation and private-link behavior. |
| Upload | File/context remain visible during upload and synchronous processing. Failure retains the chosen file. Stored Uploaded/Processing/Ready/Failed states use real server metadata. |
| Study Assistant | Explicit Generating answer / Creating quiz draft / Creating flashcards / Explaining answer labels. Context and previous output remain visible; existing one-flight generation and explicit save controls preserved. |
| Analytics | Keeps summary/chart/history snapshots while ranges/pages resolve or fail; labels retained results. Sections update independently, with date ranges still visible. |
| Settings | Existing account data stays visible; initial profile-timezone lookup is identified locally. Documented fallback/retry behavior unchanged. |
| Login/session bootstrap | Audited without changing auth behavior. Existing bootstrap, transient failure, refresh, identity-switch and sign-out regressions pass. |

## Verification

- All 14 frontend test files pass, including new initial-versus-refresh, retained-chart, retained-calendar, independent assessment-history and rapid-save regressions.
- TypeScript and optimized Next.js build pass; existing routes compile.
- Browser interception held and failed reads to check cold loading, Dashboard retry, Analytics range changes, Planner month/week changes and persistent authenticated navigation. No replacement skeletons or blank calendars/charts appeared during those refreshes.
- Intercepted AI generation and multipart upload requests verified pending labels, input/file retention, error recovery and single-flight submission. No Gemini calls or resource/study writes were made by these checks.
- Desktop retained-content and mobile upload-pending screens were visually reviewed. Temporary auth accounts and browser profiles were removed. Screenshots, local harnesses and raw reports remain ignored.

## Known limits

- The upload endpoint performs transfer and parsing within one request and does not expose byte progress or processing-stage events. The UI describes the combined wait honestly; it does not simulate percentages or infer a stage from elapsed time.
- Retained snapshots are explicitly identified and may be stale until a successful refresh. Existing dependent write controls remain serialized where parallel writes would conflict with current recovery behavior.
- This pass uses focused browser and regression checks, not physical-device testing or a fresh live CRUD test of every unchanged backend domain.
