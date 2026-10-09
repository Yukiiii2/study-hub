"""Synchronous resources boundary: parsing, owner access and storage compensation."""
import logging
import re
from uuid import uuid4

from app.parsers.csv_parser import parse_csv
from app.parsers.pdf_parser import parse_pdf
from app.repositories import resources as repo
from app.schemas.resources import ResourceResponse, UploadMetadata
from app.services.resource_errors import MAX_FILE_BYTES, ResourceError
from app.services.resource_storage import BUCKET, ResourceStorage

logger = logging.getLogger(__name__)
TYPE_ERROR = "Only PDF and CSV files with matching file types are supported."
CSV_MIMES = {"text/csv", "application/csv", "application/vnd.ms-excel"}


def _filename(filename):
    if not filename or len(filename) > 1000 or any(ord(c) < 32 for c in filename):
        raise ResourceError(422, "Invalid upload fields.")
    leaf = filename.replace("\\", "/").rsplit("/", 1)[-1].strip()
    if len(leaf) > 255:
        raise ResourceError(422, "Invalid upload fields.")
    extension = leaf.rsplit(".", 1)[-1].lower() if "." in leaf else ""
    if extension not in {"csv", "pdf"}:
        raise ResourceError(415, TYPE_ERROR)
    stem = re.sub(r"[^A-Za-z0-9 _().-]", "_", leaf.rsplit(".", 1)[0]).strip(" .") or "resource"
    return leaf, stem[:155] + "." + extension, extension


def _required(row):
    if row is None:
        raise ResourceError(404, "Resource not found.")
    return row


def _private_path(row, user_id):
    path = row.get("storage_path")
    prefix = f"{user_id}/{row['id']}/"
    if row.get("storage_bucket") != BUCKET or not isinstance(path, str) or not path.startswith(prefix) or not re.fullmatch(r"[A-Za-z0-9 _().-]+\.(pdf|csv)", path[len(prefix):]):
        raise ResourceError(503, "Resources are unavailable. Try again.")
    return path


def upload_resource(user_id, filename, mime, data, metadata: UploadMetadata, *, storage=None):
    if len(data) > MAX_FILE_BYTES:
        raise ResourceError(413, "Files must be 4 MiB or smaller.")
    if not data:
        raise ResourceError(422, "Invalid upload fields.")
    filename, object_name, kind = _filename(filename)
    mime = (mime or "").split(";", 1)[0].strip().lower()
    if (kind == "pdf" and (mime != "application/pdf" or not data.startswith(b"%PDF-"))) or (kind == "csv" and mime not in CSV_MIMES):
        raise ResourceError(415, TYPE_ERROR)
    resource_id = uuid4()
    path = f"{user_id}/{resource_id}/{object_name}"
    values = {"id": resource_id, "subject_id": metadata.subject_id, "topic_id": metadata.topic_id,
              "title": metadata.title or object_name.rsplit(".", 1)[0], "original_filename": filename,
              "mime_type": "application/pdf" if kind == "pdf" else "text/csv", "file_size_bytes": len(data),
              "storage_bucket": BUCKET, "storage_path": path, "resource_type": kind,
              "processing_status": "uploaded", "page_count": None, "row_count": None, "error_message": None}
    sections = []
    if kind == "csv":
        if data.startswith((b"%PDF-", b"PK\x03\x04", b"MZ", b"\x7fELF", b"\x89PNG")):
            raise ResourceError(422, "CSV contains unsupported binary content.")
        values["row_count"] = parse_csv(data).row_count
    storage = storage or ResourceStorage()
    upload_attempted = False
    try:
        with repo.transaction() as connection:
            if not repo.valid_associations(connection, metadata.subject_id, metadata.topic_id):
                raise ResourceError(422, "Choose an active subject and its matching topic.")
            # A lost provider response may follow a successful object write.
            # This generated path is new, so compensate even an uncertain upload.
            upload_attempted = True
            storage.upload(path, data, values["mime_type"])
            repo.insert_resource(connection, user_id, values, [])
            repo.mark_processing(connection, user_id, resource_id)
            if kind == "pdf":
                parsed = parse_pdf(data)
                values.update(processing_status=parsed.processing_status, page_count=parsed.page_count, error_message=parsed.error_message)
                sections = parsed.sections
                if parsed.processing_status == "failed":
                    logger.warning("resource_pdf_processing_failed resource_id=%s", resource_id)
            else:
                values["processing_status"] = "ready"
            row = repo.finish_processing(connection, user_id, resource_id, values, sections)
            # Validate before transaction commit so invalid DB responses also compensate.
            result = ResourceResponse.model_validate(row)
        return result
    except Exception:
        if upload_attempted:
            try:
                storage.delete(path)
            except Exception:
                logger.error("resource_upload_cleanup_failed resource_id=%s", resource_id)
        raise


def list_resources(user_id, **filters):
    with repo.transaction() as connection:
        return repo.list_resources(connection, user_id, **filters)


def get_resource(user_id, resource_id):
    with repo.transaction() as connection:
        return _required(repo.get_resource(connection, user_id, resource_id))


def delete_resource(user_id, resource_id, *, storage=None):
    storage = storage or ResourceStorage()
    with repo.transaction() as connection:
        row = _required(repo.get_resource(connection, user_id, resource_id, lock=True, private=True))
        storage.delete(_private_path(row, user_id))
        # If DB commit fails after deletion, metadata remains and a missing-object
        # retry can finish. Provider failure always keeps metadata and sections.
        repo.delete_resource(connection, user_id, resource_id)


def download_resource(user_id, resource_id, *, download=True, storage=None):
    with repo.transaction() as connection:
        row = _required(repo.get_resource(connection, user_id, resource_id, private=True))
        path = _private_path(row, user_id)
    return {"url": (storage or ResourceStorage()).sign(path, download=download), "expires_in": 120}


def resource_content(user_id, resource_id, *, limit=10, offset=0, storage=None):
    with repo.transaction() as connection:
        row = _required(repo.get_resource(connection, user_id, resource_id, private=True))
        path = _private_path(row, user_id)
        sections, total = repo.content_sections(connection, user_id, resource_id, limit=limit, offset=offset)
    result = {"resource": ResourceResponse.model_validate(row), "sections": sections, "headers": [],
              "rows": [], "row_count": row["row_count"], "total_sections": total}
    if row["resource_type"] == "csv":
        try:
            csv = parse_csv((storage or ResourceStorage()).read(path))
        except ResourceError as error:
            if error.status_code == 503:
                raise
            raise ResourceError(503, "Resources are unavailable. Try again.") from None
        result.update(headers=csv.headers, rows=csv.rows, row_count=csv.row_count)
    return result
