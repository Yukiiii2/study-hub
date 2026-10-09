# IMPORTS.md

## Purpose

Defines how the existing spreadsheet and future PDF/CSV uploads enter CPA Study Hub.

## General pipeline

```text
source
 -> detect/select type
 -> parse
 -> normalize
 -> validate
 -> preview
 -> commit
 -> report
```

Never silently discard invalid data.

## Existing Google Sheet / XLSX migration

### Implemented Phase 4: Project 1 curriculum

The approved source is the local, Git-ignored `data/imports/Project 1.xlsx`. The CLI is `backend/app/services/curriculum_import.py`; literal workbook parsing and explicit mapping live in `backend/app/parsers/curriculum_workbook.py`. Install the separate `backend/requirements-import.txt` for local migration tooling; the API runtime does not need the XLSX reader.

From `backend/`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-import.txt
# Default is a read-only dry run.
.\.venv\Scripts\python.exe -m app.services.curriculum_import
# Review the report and resolve critical errors before explicit commit mode.
.\.venv\Scripts\python.exe -m app.services.curriculum_import --commit --approved-plan ../data/imports/reports/project-1-dry-run.plan.json --report ../data/imports/reports/project-1-migration.md
# Required independent idempotency check after migration.
.\.venv\Scripts\python.exe -m app.services.curriculum_import --report ../data/imports/reports/project-1-second-dry-run.md
```

`--workbook` and `--report` accept explicit paths. Reports and manifests are generated locally; commit only reviewed, safe Markdown reports. Generated JSON manifests/auxiliary plans and personal source workbooks are ignored. Never commit real environment files. Reports omit personal progress, recall history, remarks, calendar events, and credentials.

Mapping: `MS -> MAS`; `FAR`, `AFAR`, `TAX`, `RFBT`, `AT`, and `AP` map to their existing subject codes. Main sheets must have `HO#`/`Sub-topics` in B2/C2; curriculum comes only from literal B/C values after row 3. Code sheets corroborate each accepted code/title; they are not a second topic source. Formula/error cells in curriculum fields block import. Blank/header/formatting rows are skipped. Source spelling, punctuation, and code case remain unchanged; only whitespace is normalized. Notes/Drills/REO Live and personal progress cells are not descriptions.

Approved exclusions: `FAR!B22` (`FAR-19`) and `FAR!B39` (`FAR-36`) lack usable titles. No replacement names are invented. All parent relationships remain null: no explicit main-sheet parent or indentation exists, and dotted/letter codes alone are treated conservatively. `display_order` is the original source row number, retaining gaps and traceability.

Identity is existing subject UUID plus exact source code. New IDs use UUIDv5 with `NAMESPACE_URL` and `study-hub/project-1/curriculum/v1/{subject UUID}/{source code}`. Existing code matches keep their IDs. Duplicate/case-colliding codes or differences in code spacing/case, title, description, parent, or order are blocking conflicts. There are no updates, deletes, subject inserts, or schema changes. Reruns report identical records as unchanged rather than overwrite them.

Dry run checks subjects and existing topic integrity in a read-only repeatable-read transaction. Commit requires that successful plan's fingerprint to match a freshly parsed workbook, mapping, and database snapshot while subject/topic table locks are held. All inserts and post-write checks occur in one transaction; validation failure rolls back. Source/database changes require a new reviewed dry run. The approved import accepted FAR 43, AFAR 15, MAS 18, TAX 27, RFBT 23, AT 17, and AP 20 topics (163 total).

Video sheets are mapped by exact topic code and literal lecture title; raw XML duration values, decoded types, and number formats remain available without assuming duration units. RFBT Vids references `RFBT-11A`, differing from curriculum `RFBT-11a`; TAX Vids C64 is nonnumeric. Recall uses exact normalized-title matching; AP Recall A6 differs from the curriculum title. R1–R5 is not translated into an algorithm. Assessments preserve literal section names/coverage and flag nonmatching titles. Schedule `AT/AUD` is unresolved between AT/AP; Calendar requires full month/date-grid context. All these domains are report-only; their production tables and UI remain deferred.

See the reviewed reports in `data/imports/reports/` for workbook inventory, accepted rows, skips, warnings, and second-run results.

The current workbook is the initial content source.

Logical areas include:

- Schedule
- Calendar
- Progress Overview
- Assessments
- per-subject tracking
- per-subject video tracking
- per-subject recall tracking
- per-subject code/reference tracking

Known subject families include:

- MAS / MS
- AT
- AP
- RFBT
- TAX
- FAR
- AFAR

Map spreadsheet structures into normalized entities instead of creating one table per worksheet.

### Mapping concept

Subject overview sheets:
- subjects/topics
- supported user progress metadata

`* Vids`:
- videos
- user video progress

`* Recall`:
- historical recall source data
- later transformed only after mapping rules are explicit

Schedule:
- study events / recurrence templates

Assessments:
- assessments and assessment-topic coverage

Do not automatically migrate ambiguous cells. Produce a migration report.

### Migration workflow

1. Export/materialize workbook.
2. Inspect sheet names/headers.
3. Build explicit mapping.
4. Normalize rows.
5. Validate references.
6. Produce dry-run summary.
7. Commit only after mapping is approved.

Report:

- sheets detected
- rows processed
- entities created
- skipped rows
- warnings
- unresolved mappings

## Implemented Phase 5: Project 1 lectures

`backend/app/parsers/video_workbook.py` extends the existing curriculum parser, mapping constants, raw-duration extraction, and source traceability. `backend/app/services/video_import.py` reuses the curriculum state reader, validation, and fingerprint approach. The same local import requirements apply; no new API/runtime dependencies are needed. Apply Alembic revision `0003_video_tracking` before the database-aware video dry run.

From `backend/`:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m app.services.video_import
# Review the dry-run report before explicit commit mode.
.\.venv\Scripts\python.exe -m app.services.video_import --commit --approved-plan ../data/imports/reports/project-1-video-dry-run.plan.json --report ../data/imports/reports/project-1-video-migration.md
.\.venv\Scripts\python.exe -m app.services.video_import --report ../data/imports/reports/project-1-video-second-dry-run.md
# Focused duration, real-source mapping, idempotency/conflict, and API boundary checks:
.\.venv\Scripts\python.exe -m unittest tests.test_video_import tests.test_videos
```

The workbook remains `data/imports/Project 1.xlsx`, private and ignored. `--workbook`/`--report` accept other paths, but the parser is deliberately specific to this reviewed workbook family. JSON manifests stay local. Safe Markdown reports omit credentials and personal progress/history.

Lecture candidates come from literal A topic reference / B title / C duration on all seven `* Vids` sheets with verified headers. Uncoded section labels, Total Time rows, formatting blanks, and formula-only count summaries with blank title/duration are skipped and reported. Formula/error values in lecture fields block migration. MS normalizes to MAS. Relationships require exact existing topic codes; the sole approved alias is RFBT-11A to existing RFBT-11a at RFBT Vids rows 98–99. Current Phase 4 topics must match the curriculum source; no topic is created or retitled by this importer.

The client confirmed displayed lecture units: `h:mm` cells represent MM:SS, and `[h]:mm:ss` cells with zero stored final seconds represent elapsed MM:SS (stored 57:27:00 means a 57m27s lecture). `h:mm:ss` represents real HH:MM:SS. Raw XML serials retain elapsed hours before openpyxl conversion; those components reconstruct the confirmed display units, rather than treating lecture values as Excel time-of-day durations. All accepted values become integer seconds, with 0.01 stored-second rounding tolerance. Explicit confirmed corrections require original cell/value matches: FAR C294 23.59 -> 23:59, FAR C295 24.46 -> 24:46, TAX C64 27:08: -> 27:08. Any other malformed/unconfirmed duration is reported and its video skipped until confirmed; negative, wrapped, and unexpected formats are rejected.

Approved unresolved conflict: FAR Vids rows 586–587 both contain `42-04 Exercise 2` (FAR-42), with durations 48:23 and 48:22. Both remain excluded until client/source clarification. No merge, renamed title, or invented distinguishing identity is used to import them.

Identity: topic UUID + `project-1:worksheet:row` locator stored as `source_code`; this is migration provenance, not an invented curriculum/lecture code. UUIDv5 uses `NAMESPACE_URL` and `study-hub/project-1/videos/v1/{topic UUID}/{locator}`. Display order is the original source row. Exact existing matches retain their IDs. Changed title/duration/topic/order/URL, duplicate source locators/titles, and relocated rows colliding with existing identities/titles block writes rather than overwrite. Row reorder/source edits require a fresh dry run and explicit conflict resolution.

Default mode is read-only repeatable-read. Commit requires a matching successful source/mapping/database fingerprint, rechecked under subject/topic/video locks. Inserts and full post-write verification share one transaction; errors roll back. No updates, deletes, user progress writes, or subject/topic writes. A second dry run must propose zero inserts; this source yields 1,562 unchanged videos. Counts: FAR 482, AFAR 185, MAS 155, TAX 200, RFBT 107, AT 108, AP 325.

Workbook completion checkboxes and other personal source states are not read into tracking. Progress starts derived/lazy for each authenticated user. Recall, schedule/calendar, and assessments remain source-report-only. Phase 6 creates user-owned planner tables separately without transferring the workbook schedule.

Reports: [video dry run](data/imports/reports/project-1-video-dry-run.md), [video migration](data/imports/reports/project-1-video-migration.md), [video second dry run](data/imports/reports/project-1-video-second-dry-run.md).

## Phase 6: schedule / calendar dry run

The read-only CLI `python -m app.services.schedule_inspect` from `backend/` uses the existing optional import requirements and defaults to `data/imports/Project 1.xlsx`. Optional `--workbook` and `--report` paths are supported. It has no database access or commit mode. The [safe report](data/imports/reports/project-1-schedule-dry-run.md) records the source hash, layout, counts and source-code/reference conflicts, omitting literal personal calendar contents/dates, remarks and completion state.

SCHEDULE has 19 complete literal seven-day header blocks (133 dates); topic-reference rows may extend beyond three rows, so all direct curriculum references are inspected structurally. 152 of 153 resolve to accepted source topic rows. Thirteen cross the weekday-column subject; one direct reference is unresolved, and three indirect references need separate tracing. MS maps to MAS; the AT/AUD column is not a unique subject, while explicit AT/AP references remain distinguishable.

Calendar has nine month headers and 273 validated day cells. The reproducible inspector counts nonblank literal text cells below date headers (including notes), rather than normalized events. Month/date/weekday alignment is checked without executing formulas. Neither sheet provides exact study start/end times. Helper countdowns, assessment labels, breaks/reminders and workbook completion are not converted into timed records or personal progress.

Decision: zero event/task/session inserts or updates; both sheets remain report-only. Preserve the weekday pattern in the report and let the authenticated user configure actual times through Study Plan. Future source conversion requires confirmed ownership, activity meaning and ambiguous relationships; no fake midnight events or automatic task assignments.

## PDF

### Implemented Phase 7 resource uploads

Upload through `POST /api/resources/upload`; the original is retained in private
Supabase Storage, not the repository. Limit 4 MiB; filename extension, declared
MIME and actual content are checked. Storage uses server-generated user/resource
UUID paths and sanitized filenames, while metadata preserves the submitted name.
The Library upload is file preservation/processing, not a bulk domain import.

PDF text extraction uses pypdf, preserving page number and order in
document_sections. Empty pages remain identifiable. No extractable text produces
a failed processing status explaining possible scanned/image content. Unreadable
or encrypted documents produce safe errors; no OCR, tables or images are fabricated.
Parsing is isolated, synchronous and bounded; larger jobs require a future worker.

PDF processing accepts at most 200 pages, 20,000 text characters per page and
1,000,000 overall. Decoded streams are bounded to 2,000,000 bytes each and
20,000,000 cumulatively, including repeated Form invocations (at most 200 per
page). Exceeding these bounds produces a failed status, not truncated ready text.

CSV uses Python's standard csv module with strict UTF-8/BOM decoding and
comma-separated header/row/quote validation. Bounds are 100 columns, 200 header
characters, 10,000 characters per cell, 100,000 data rows and 200,000 preview
characters. The preview contains at most 20 rows. Other delimiters/encodings
require a later explicit format contract. Metadata stores row count; the original stays in
Storage. Content requests reconstruct previews without permanently persisting
arbitrary rows. Malformed input is rejected and never imported into other domains.
Quiz/flashcard CSV templates later in this document remain unimplemented contracts.

Initial support: text-based/selectable-text PDFs.

Store:

- original file
- filename
- MIME type
- size
- page count when available
- subject/topic link
- processing status
- extracted text
- page-aware sections/chunks

### Source grounding

Generated quiz/flashcard/AI content should keep when available:

- resource_id
- page number/range
- section id
- source metadata

Do not claim exact page grounding if parser output cannot support it.

### Deferred PDF support

- OCR/scanned PDF
- handwriting
- complex visual table interpretation
- image-only understanding

## CSV

### Quiz CSV

Implemented Phase 8, independently of Library file uploads. Use
`POST /api/imports/questions/preview` with multipart file, then explicitly confirm
with `/commit`, reuploading the same file and its preview_token. The signed token
binds the user/file and expires after 15 minutes. Commit revalidates all rows,
ownership and duplicates inside a transaction; errors block the entire import.
No Storage object or resource row is created by this dedicated import.

UTF-8/BOM comma CSV only, at most 1 MiB and 500 data rows. The header-only
template is `data/templates/questions.csv`. Required fields are question and
correct_answer. Optional fields: subject, topic, question_type, option_a through
option_f, explanation, resource_id and source_page. Type defaults to single_select;
multi_select uses semicolon-separated correct keys (A–F). True/false uses blank
option columns and TRUE/FALSE keys. Subject codes map to existing subjects,
including MS -> MAS; topic uses its unique code in that subject. Unknown or
ambiguous mappings are errors, never invented. Source resource/page must be owned
and valid. No arbitrary CSV domain import, flashcards or AI generation.

Dry run reports row/valid/duplicate counts, proposed inserts, unchanged rows,
warnings/errors with row/field/reason, and at most 20 sample records. Identity is
owner + subject/topic + whitespace-normalized prompt; full canonical content
fingerprints distinguish identical rows from conflicting options/keys/type/source
or explanation. Exact duplicates are reported and skipped; conflicts reject the
commit rather than overwriting. A second identical import proposes zero inserts.

Supported question import columns:

```text
subject
topic
question_type
question
option_a
option_b
option_c
option_d
option_e
option_f
correct_answer
explanation
resource_id
source_page
```

Validate question, answer, options, subject/topic mapping, encoding, duplicates, and syntax.

### Flashcard CSV

```text
subject
topic
front
back
```

Validate front/back, mapping, and duplicates.

### Topic CSV

```text
subject
code
topic
status
```

Do not assign status semantics until the progress model is defined.

## Preview-first rule

Bulk import preview must report:

- detected/import-selected type
- row count
- valid rows
- warnings
- errors
- mapped columns
- sample rows

Commit validates again server-side.

## Errors

Identify:

- row
- field
- reason
- suggested correction when obvious

## Duplicates

Behavior must be explicit per importer: skip, update, or duplicate.

Early default: detect/report duplicates and require a decision before bulk update.

## Security

- validate MIME/extension
- enforce size limits
- sanitize filenames
- generate storage paths
- never execute uploads
- protect private storage references
