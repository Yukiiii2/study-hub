"""Dedicated, bounded question CSV endpoints; uploaded bytes never enter Storage."""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError
from starlette.concurrency import run_in_threadpool
from starlette.datastructures import UploadFile
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

from app.core.auth import CurrentUser
from app.parsers.quiz_csv_parser import MAX_FILE_BYTES, QuizImportError
from app.schemas.quizzes import QuestionInput
from app.services import quiz_import as service

router = APIRouter(prefix="/api/imports/questions", tags=["question imports"])
MAX_REQUEST_BYTES = MAX_FILE_BYTES + 16 * 1024
CSV_MIMES = {"text/csv", "application/csv", "application/vnd.ms-excel"}


class ImportIssue(BaseModel):
    row: int
    field: str
    message: str


class ImportPreview(BaseModel):
    row_count: int
    valid_count: int
    duplicate_count: int
    proposed_inserts: int
    unchanged: int
    warnings: list[ImportIssue]
    errors: list[ImportIssue]
    sample: list[QuestionInput] = Field(max_length=20)
    preview_token: str | None


class ImportResult(BaseModel):
    inserted: int
    unchanged: int


class QuestionImportBodyLimit:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        paths = {"/api/imports/questions/preview", "/api/imports/questions/commit"}
        if scope["type"] != "http" or scope["method"] != "POST" or scope["path"].rstrip("/") not in paths:
            await self.app(scope, receive, send)
            return
        oversized = JSONResponse({"detail": "Question CSV upload request is too large."}, status_code=413)
        length = dict(scope.get("headers", [])).get(b"content-length")
        if length is not None:
            try:
                length = int(length)
            except ValueError:
                await JSONResponse({"detail": "Invalid question CSV upload fields."}, status_code=422)(scope, receive, send)
                return
            if length < 0 or length > MAX_REQUEST_BYTES:
                await oversized(scope, receive, send)
                return
        chunks = []
        size = 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            chunk = message.get("body", b"")
            size += len(chunk)
            if size > MAX_REQUEST_BYTES:
                await oversized(scope, receive, send)
                return
            chunks.append(chunk)
            if not message.get("more_body", False):
                break
        consumed = False

        async def bounded_receive():
            nonlocal consumed
            if not consumed:
                consumed = True
                return {"type": "http.request", "body": b"".join(chunks), "more_body": False}
            return await receive()

        await self.app(scope, bounded_receive, send)


def _call(handler, *args):
    try:
        return handler(*args)
    except QuizImportError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from None
    except (SQLAlchemyError, ValueError):
        raise HTTPException(status_code=503, detail="Question imports are unavailable. Try again.") from None


async def _upload(request, user_id, *, commit):
    if not request.headers.get("content-type", "").lower().startswith("multipart/form-data;"):
        raise HTTPException(status_code=422, detail="Invalid question CSV upload fields.")
    try:
        async with request.form(max_files=1, max_fields=1 if commit else 0, max_part_size=2048) as form:
            allowed = {"file", "preview_token"} if commit else {"file"}
            if set(form) != allowed or any(len(form.getlist(key)) != 1 for key in form):
                raise HTTPException(status_code=422, detail="Invalid question CSV upload fields.")
            file = form.get("file")
            if not isinstance(file, UploadFile):
                raise HTTPException(status_code=422, detail="Invalid question CSV upload fields.")
            filename = file.filename or ""
            mime = (file.content_type or "").split(";", 1)[0].strip().lower()
            if not filename.lower().endswith(".csv") or mime not in CSV_MIMES:
                raise HTTPException(status_code=415, detail="Use a CSV file with a matching CSV content type.")
            if file.size is not None and file.size > MAX_FILE_BYTES:
                raise HTTPException(status_code=413, detail="Question CSV files must be 1 MiB or smaller.")
            data = await file.read(MAX_FILE_BYTES + 1)
            if len(data) > MAX_FILE_BYTES:
                raise HTTPException(status_code=413, detail="Question CSV files must be 1 MiB or smaller.")
            if commit:
                token = form.get("preview_token")
                if not isinstance(token, str) or not token or len(token) > 2048:
                    raise HTTPException(status_code=422, detail="Invalid question CSV upload fields.")
                return await run_in_threadpool(_call, service.commit_questions, user_id, data, token)
            return await run_in_threadpool(_call, service.preview_questions, user_id, data)
    except StarletteHTTPException as error:
        if isinstance(error, HTTPException):
            raise
        raise HTTPException(status_code=422, detail="Invalid question CSV upload fields.") from None


@router.post("/preview", response_model=ImportPreview)
async def question_import_preview(request: Request, user: CurrentUser):
    return await _upload(request, user.id, commit=False)


@router.post("/commit", response_model=ImportResult)
async def question_import_commit(request: Request, user: CurrentUser):
    return await _upload(request, user.id, commit=True)
