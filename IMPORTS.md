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

## PDF

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

Candidate columns:

```text
subject
topic
question
option_a
option_b
option_c
option_d
correct_answer
explanation
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
