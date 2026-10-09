# Phase 8 quiz engine and question bank

## Approved design

Extend the existing FastAPI/PostgreSQL boundary and shared authenticated Next.js
layout. Standing phase approval applies; no paid services, schema replacement,
real question imports, new dependencies or later-phase features. Existing
`frontend/next-env.d.ts` user work stays untouched and uncommitted.

Questions and quizzes are private to their verified owner. Question types are
`single_select`, `multi_select`, `true_false`. Options use stable keys (A–F for
multiple choice; TRUE/FALSE for true/false). Single-select has exactly one correct
key; multi-select has one or more and uses exact-set grading; true/false has one.
At least two distinct nonblank options are required (at most six). No partial
credit, negative marking, timer or generated content. Prompt <=5,000 characters,
option text <=1,000, explanation <=5,000. Empty answers are allowed and score zero.

Add revision `0006_quizzes` after `0005_resources`: questions, question_options,
quizzes, quiz_questions, quiz_attempts, quiz_answers. Owner composite foreign keys
protect every relation. Source resource must be owned; optional source_page must
be a real PDF page. Topic requires its matching active subject. Archive instead
of deleting questions/quizzes. Existing attempts and source history remain intact.

Each attempt freezes the ordered questions/options, keys, explanations and source
references in a private JSONB snapshot. Browser roles never receive grants for
snapshot/answer-key columns. Public taking DTOs are constructed by allowlist.
Question Bank author routes intentionally show the author's own answer keys;
this is personal study, not proctored testing. Attempt/result routes never expose
keys or explanations until completed, and another user cannot access either flow.

One active attempt per owner/quiz; start resumes it. Answers upsert by
attempt/question. Answer/save/submit lock the same attempt row. Submission grades
the snapshot atomically, sets server timestamps and persists correctness/scores;
repeat submission returns the existing result. Completed answers are immutable.
Unanswered questions count in the denominator: score_value / total_questions *100,
rounded to two decimal places. No learning-readiness formula or analytics.

Rounding uses decimal half-up to two places. Active-attempt snapshots/answers and
question option keys have no browser SELECT grants; safe question/quiz/ordering
columns have owner-only column grants. Source deletion detaches live question
references while frozen history retains its original citation.

## Shared API contract

All routes authenticated, owner derived from identity, extra fields forbidden.
404 for missing/foreign ownership; 409 for frozen/conflicting actions; validation
422; unavailable dependencies 503 with safe authored errors. Arrays bounded.

Question input: subject_id/topic_id/resource_id/source_page nullable, question_type,
prompt, explanation nullable, options:[{key,text}], correct_keys:string[].
Author Question DTO adds id, origin(manual/csv), is_archived, created_at/updated_at.

- GET /api/questions -> {questions:Question[],total}; limit50/max100, offset0;
  subject_id/topic_id/resource_id/question_type/q filters; archive excluded.
- POST /api/questions -> Question (201).
- GET /api/questions/{id} -> Question (author view).
- PATCH /api/questions/{id} -> Question; replacement question input or
  {is_archived:true} supported, no hard deletion.

Quiz input: title<=200, description nullable<=2,000, subject_id/topic_id nullable,
question_ids:string[] in order, 1..100 unique active own question IDs.
Quiz DTO: id, title, description, subject_id/topic_id, is_archived, question_count,
active_attempt_id nullable, created_at/updated_at. Detail adds questions with id,
question_type,prompt,options,subject_id/topic_id/resource_id/source_page; no keys.

- GET /api/quizzes -> {quizzes:Quiz[],total}; limit50/max100, offset0, subject_id/q.
- POST /api/quizzes -> Quiz detail (201).
- GET /api/quizzes/{id} -> Quiz detail.
- PATCH /api/quizzes/{id} -> Quiz detail; quiz input or {is_archived:true}.
- POST /api/quizzes/{id}/attempts -> Attempt; creates or resumes an active attempt.
- GET /api/quiz-attempts -> {attempts:AttemptSummary[],total}; quiz_id filter.
- GET /api/quiz-attempts/{id} -> Attempt; reload persisted answers and frozen order.
- POST /api/quiz-attempts/{id}/answers with {question_id,selected_keys:string[]}
  -> Attempt; validates snapshot membership/keys/cardinality, no grading disclosure.
- POST /api/quiz-attempts/{id}/complete -> completed Attempt/review.
- GET /api/quiz-attempts/{id}/results -> completed Attempt/review; 409 before submit.

Attempt: id,quiz_id,title,status(in_progress/completed),started_at,completed_at,
score_value nullable,total_questions,score_percent nullable,questions.
Taking question: id,question_type,prompt,options,subject_id/topic_id/resource_id/
source_page nullable,selected_keys. Completed review also adds correct_keys,
explanation,is_correct. Summary omits questions. Never return owner or snapshot.

## CSV contract

Existing upload resources remain file-preservation only. Dedicated question CSV
routes use multipart file (UTF-8/BOM comma CSV, <=1 MiB and 500 rows), no Storage.
Headers: subject,topic,question_type,question,option_a,option_b,option_c,option_d,
option_e,option_f,correct_answer,explanation,resource_id,source_page. Required:
question,correct_answer; default type single_select. Optional subject maps by
existing code (MS -> MAS), topic by unique code under that subject; ambiguous or
missing mappings are errors. TF uses blank option fields and TRUE/FALSE answers;
MC correct keys use semicolon separators. No invented associations.

Identity: owner + subject/topic + whitespace-normalized prompt. A canonical
payload fingerprint detects exact duplicates (unchanged); same identity with
different options/keys/explanation/resource/type is a conflict, never overwritten.
Within-file exact duplicates are reported/skipped. Commit is transactional and
revalidates with concurrency-safe uniqueness; any errors block all writes.

- POST /api/imports/questions/preview -> {row_count,valid_count,duplicate_count,
  proposed_inserts,unchanged,warnings:Issue[],errors:Issue[],sample:QuestionInput[],
  preview_token:string|null}; Issue={row,field,message}; at most20 samples.
- POST /api/imports/questions/commit multipart file + preview_token ->
  {inserted,unchanged}; token signed with existing backend secret, user/file-bound,
  15-minute expiry; invalid/expired token rejected. No preview rows auto-saved.

## UI and implementation plan

Use existing fonts/colors, compact lists and native dialogs. /quizzes lists quizzes
and history, /quizzes/new and /quizzes/[id] provide an ordered question builder and
start/resume; /quizzes/attempts/[id] is one-question taking/review with persisted
save state and submission confirmation. /question-bank provides manual create/edit,
archive, source/subject/topic selection and CSV preview/confirm import. Routes stay
inside (app), no new auth guard, polling or provider; failed saves never advance.

Unsaved selections have a bounded per-attempt sessionStorage recovery record
(question ID, selected keys and their saved baseline only). Browser Back/Forward
or reload can restore them with an explicit unsaved notice; changed server
baselines and completed attempts discard stale recovery records. Confirmed saves
clear matching backups. If browser storage is unavailable, the UI explicitly
instructs the user to save before leaving. No tokens, prompts, explanations or
correct-answer keys enter this recovery cache; PostgreSQL remains authoritative.

- [x] Backend core: focused red/green validation/grading/projection tests; migration,
  schemas, repositories, services, routes, own-resource associations and snapshots.
- [x] CSV: focused parser/token/duplicate tests; dedicated bounded preview/commit
  routes; safe empty-header template under data/templates, no real data import.
- [x] Frontend: services, bank/editor/import, quiz builder/taker/history/review,
  routes/nav/styles; focused states/answer-protection checks and build/TypeScript.
- [x] Integration: inspect DB; review/apply additive migration; two synthetic
  Auth users, question/quiz flows, answer reload, snapshot edits, exact grading,
  repeat submit, answer tampering/cross-user denial, RLS/grants and CSV rerun.
  Cleanup only created quiz rows/accounts/resources; never touch existing data.
- [x] Review and update DATABASE/API/IMPORTS/DATA_AND_TELEMETRY/README/ROADMAP and
  ARCHITECTURE where relevant.

Completion uses phase files only, a credential/private-file scan, the commit
`feat: add quiz engine and question bank`, then pushes main and stops.

Review focus: snapshots leaking keys before submission; concurrent save/submit;
author edits changing past results; imported identity conflicts; source ownership
and topic mapping; failed saves/fetches losing question state on navigation.

## Validation completed 2026-10-09

- Applied additive `0006_quizzes` to the configured database; all six tables have
  owner RLS, no browser mutation grants and no direct key/snapshot/answer grants.
- 44 focused backend tests passed from `backend/` using
  `.venv/Scripts/python.exe -m unittest tests/test_quizzes.py tests/test_quiz_import.py`.
- `node frontend/tests/quizzes.cjs` passed: API contracts, hidden active answers,
  retained error states, save-before-navigation, draft recovery (including denied
  browser storage), editor/import/review rendering and profile timezone display.
- `npm.cmd run build` in `frontend/` passed production compilation and TypeScript.
- `backend/.venv/Scripts/python.exe scripts/verify_quizzes.py --run` passed authenticated
  two-user API/database checks: all three formats, real associations, ordering,
  resume/reload, snapshot isolation, unanswered/exact-set grading, history/review,
  cross-user denial, input tampering, concurrent completion/save serialization,
  RLS/grants, archive preservation and transactional CSV conflict rejection.
- A synthetic 500-row CSV imported once; a second preview proposed zero inserts
  and 500 unchanged rows. A 100-question quiz preserved order and graded on the
  server. Created questions/quizzes/attempts/resources and Auth users were removed;
  cleanup verified zero surviving fixture rows without touching existing users.
- Frontend validation uses focused rendering/state checks and a production build;
  interactive browser end-to-end testing was not performed. No real question data,
  source workbook, PDF/CSV uploads or credentials were committed.
