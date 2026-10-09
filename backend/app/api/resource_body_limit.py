"""Bound only resource uploads before Starlette consumes multipart data."""
from starlette.responses import JSONResponse

from app.services.resource_errors import MAX_REQUEST_BYTES


class ResourceUploadBodyLimit:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] != "POST" or scope["path"].rstrip("/") != "/api/resources/upload":
            await self.app(scope, receive, send)
            return
        oversized = JSONResponse({"detail": "Upload request is too large."}, status_code=413)
        headers = dict(scope.get("headers", []))
        content_length = headers.get(b"content-length")
        if content_length is not None:
            try:
                length = int(content_length)
            except ValueError:
                await JSONResponse({"detail": "Invalid upload fields."}, status_code=422)(scope, receive, send)
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
        body = b"".join(chunks)
        consumed = False

        async def bounded_receive():
            nonlocal consumed
            if not consumed:
                consumed = True
                return {"type": "http.request", "body": body, "more_body": False}
            return await receive()

        await self.app(scope, bounded_receive, send)
