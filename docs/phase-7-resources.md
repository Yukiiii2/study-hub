# Phase 7 resource library design and implementation plan

## Contract

Implement only the user's Phase 7 resource library. Existing shared auth, dashboard,
planner and curriculum stay intact. PostgreSQL stores metadata/PDF sections;
private Supabase Storage stores originals. FastAPI owns all mutations and parsing.
No domain CSV import, OCR, AI, embeddings, quizzes or flashcards.

Uploads: at most 4 MiB (4,194,304 bytes), with a separate bounded multipart request
limit. This leaves overhead under Vercel's 4.5 MB request ceiling. Validate filename
extension, declared MIME and content; normalize stored MIME. Use pypdf and
python-multipart only; CSV uses the standard library. Reject malformed CSV before
storage. Retain valid PDF originals with failed processing metadata when extraction
fails or no text exists. Bound page count, extracted text and preview responses.

Add revision 0005_resources after 0004_study_planner. resources fields follow the
user prompt (file_size_bytes, row_count, error_message included). Sections use
page_number, section_index, content; one section per PDF page. Composite topic /
subject relationship and owner SELECT RLS follow current migrations. Browser
mutation grants remain denied. Storage SELECT requires the user-scoped path and
matching own resource metadata; no browser write policies. Create/verify private
study-resources bucket through Storage API, not direct storage metadata SQL.

Ownership uses verified UUID exclusively. Never return owner, bucket/path or keys
in metadata. Storage paths: user UUID/resource UUID/sanitized filename. No upsert.
Signed links expire after 120 seconds. Upload compensation removes newly uploaded
objects when metadata insertion fails; cleanup failures are safely logged. Delete
holds an owner row lock, removes storage first, then cascades sections/metadata;
storage failure retains database records. Storage and PostgreSQL are not a shared
transaction: database failure after storage removal must report failure and allow
an idempotent deletion retry. Never silently claim success on provider failure.

## API contract

All routes authenticated under /api/resources. Multipart upload fields file, title,
subject_id, topic_id; supplied ownership/path fields rejected. Topic requires its
active matching subject. Sanitized errors: 401 absent/invalid auth, 404 missing or
other-user record, 413 size, 415 unsupported type, 422 input/CSV/association,
503 storage/database. Upload returns 201 resource metadata, including failed PDFs.

Resource DTO: id, subject_id, topic_id, subject_code, topic_title (nullable), title,
original_filename, mime_type, file_size_bytes, resource_type (pdf/csv),
processing_status (uploaded/processing/ready/failed), page_count, row_count,
error_message (nullable), created_at, updated_at.

- GET list: {resources: Resource[], total: number}; filters subject_id, topic_id,
  resource_type, q; limit default 50/max100, offset default0. Newest first.
- POST /upload: Resource.
- GET /{id}: Resource.
- DELETE /{id}: 204.
- GET /{id}/download: {url: string, expires_in: 120}; optional download bool true
  default, false opens PDF; links must remain transient and not logged.
- GET /{id}/content: {resource: Resource, sections: Section[], headers: string[],
  rows: string[][], row_count: number|null, total_sections: number}; PDF pagination
  offset0, limit10/max20; CSV at most first20 rows, reparsed from private original.
  Section: id, page_number, section_index, content.

## UI

Functional Library nav, /library compact resource list/filter/search/pagination,
file picker upload dialog with optional title and subject-filtered topic choice;
/library/[resourceId] metadata, download/open, confirmed deletion, extracted PDF
text by page or scrollable CSV preview. Reuse API token recovery for multipart,
without new providers/guards/listeners. Page-level loading, retryable errors and
honest empty states. Preserve current fonts/colors/focus rules, mobile stacked rows.

## Execution and checks

- [x] Backend: add focused parser/API/failure tests first; implement migration,
  repositories, storage service, parsers, DTOs and routes; run focused unit tests.
- [x] Frontend: multipart API recovery checks first, then services/list/upload/
  detail/routes/navigation/styles; run focused checks and build/TypeScript.
- [x] Integration: apply additive migration; safely create or verify bucket;
  temporary authenticated-user PDF/CSV lifecycle checks, invalid files/oversize,
  relationships, other-user denial, SQL RLS and Storage policy checks. Remove only
  synthetic verification accounts/resources. Never print credentials/private files.
- [x] Update ARCHITECTURE, DATABASE, API, IMPORTS, DATA_AND_TELEMETRY, README,
  DEPLOYMENT, ROADMAP; review complete diff and failure recovery/security.
- [ ] Stage Phase 7 code/docs/migrations only; exclude real env/workbook/uploads,
  generated files and the existing next-env.d.ts user edit. Commit once with
  feat: add resource library and file processing; push origin/main, no force.

Review focus: cross-user identifiers, request/decoded-output bounds, malformed
CSV quoting/row shapes, renamed binary files, storage/DB failure ordering and
unchanged auth recovery during multipart retries.

## Verification completed (2026-10-09)

Focused backend resource checks: 24 passed, including malformed quoting, multipart
bounds, nested/indirect PDF Forms, empty PDF metadata and uncertain-upload cleanup.
Frontend: 11 authenticated API recovery checks, resource rendering/state checks,
and production build with TypeScript passed. Library list/detail route responses
passed; interactive browser verification was unavailable.

Applied `0005_resources`, verified resource tables/RLS and private bucket settings.
The live script passed two-user PDF/CSV upload, extraction/preview/counts, invalid
files/size/associations, owner isolation, signed downloads, SQL RLS and Storage
read/write isolation, then authenticated deletion. Synthetic metadata, sections,
objects and temporary Auth accounts were cleaned up. No private fixtures saved.
