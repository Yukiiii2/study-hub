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
