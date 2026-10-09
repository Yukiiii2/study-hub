from functools import wraps
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request, Response
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.concurrency import run_in_threadpool
from starlette.datastructures import UploadFile
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.auth import CurrentUser
from app.schemas.resources import ResourceContent, ResourceDownload, ResourceList, ResourceResponse, UploadMetadata
from app.services import resources as service
from app.services.resource_errors import MAX_FILE_BYTES, ResourceError

router = APIRouter(prefix="/api/resources", tags=["resources"])


def boundary(handler):
    @wraps(handler)
    def guarded(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except ResourceError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from None
        except (SQLAlchemyError, ValueError):
            raise HTTPException(status_code=503, detail="Resources are unavailable. Try again.") from None
    return guarded


@router.get("", response_model=ResourceList)
@boundary
def resource_list(user: CurrentUser, subject_id: UUID | None = None, topic_id: UUID | None = None,
                  resource_type: Literal["pdf", "csv"] | None = None,
                  q: Annotated[str | None, Query(max_length=200)] = None,
                  limit: Annotated[int, Query(ge=1, le=100)] = 50,
                  offset: Annotated[int, Query(ge=0)] = 0):
    return service.list_resources(user.id, subject_id=subject_id, topic_id=topic_id,
                                  resource_type=resource_type, q=q, limit=limit, offset=offset)


@router.post("/upload", response_model=ResourceResponse, status_code=201)
async def resource_upload(request: Request, user: CurrentUser):
    if not request.headers.get("content-type", "").lower().startswith("multipart/form-data;"):
        raise HTTPException(status_code=422, detail="Invalid upload fields.")
    try:
        async with request.form(max_files=1, max_fields=3, max_part_size=2048) as form:
            allowed = {"file", "title", "subject_id", "topic_id"}
            if any(key not in allowed or len(form.getlist(key)) != 1 for key in form):
                raise HTTPException(status_code=422, detail="Invalid upload fields.")
            file = form.get("file")
            if not isinstance(file, UploadFile):
                raise HTTPException(status_code=422, detail="Invalid upload fields.")
            fields = {key: value for key, value in form.items() if key != "file"}
            if any(not isinstance(value, str) for value in fields.values()):
                raise HTTPException(status_code=422, detail="Invalid upload fields.")
            try:
                metadata = UploadMetadata.model_validate(fields)
            except ValidationError:
                raise HTTPException(status_code=422, detail="Invalid upload fields.") from None
            if file.size is not None and file.size > MAX_FILE_BYTES:
                raise HTTPException(status_code=413, detail="Files must be 4 MiB or smaller.")
            data = await file.read(MAX_FILE_BYTES + 1)
            return await run_in_threadpool(boundary(service.upload_resource), user.id, file.filename, file.content_type, data, metadata)
    except StarletteHTTPException as error:
        # Multipart parser failures may quote private headers; expose one safe message.
        if isinstance(error, HTTPException):
            raise
        raise HTTPException(status_code=422, detail="Invalid upload fields.") from None


@router.get("/{resource_id}", response_model=ResourceResponse)
@boundary
def resource_get(resource_id: UUID, user: CurrentUser):
    return service.get_resource(user.id, resource_id)


@router.delete("/{resource_id}", status_code=204)
@boundary
def resource_delete(resource_id: UUID, user: CurrentUser):
    service.delete_resource(user.id, resource_id)
    return Response(status_code=204)


@router.get("/{resource_id}/download", response_model=ResourceDownload)
@boundary
def resource_download(resource_id: UUID, user: CurrentUser, download: bool = True):
    return service.download_resource(user.id, resource_id, download=download)


@router.get("/{resource_id}/content", response_model=ResourceContent)
@boundary
def resource_content(resource_id: UUID, user: CurrentUser,
                     limit: Annotated[int, Query(ge=1, le=20)] = 10,
                     offset: Annotated[int, Query(ge=0)] = 0):
    return service.resource_content(user.id, resource_id, limit=limit, offset=offset)
