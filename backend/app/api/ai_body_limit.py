"""Bound AI JSON before request parsing, including streamed/chunked bodies."""
from starlette.responses import JSONResponse

PATHS = {"/api/ai/ask", "/api/ai/generate-quiz", "/api/ai/generate-flashcards", "/api/ai/explain-answer"}
MAX_REQUEST_BYTES = 32 * 1024


class AIBodyLimit:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] != "POST" or scope["path"].rstrip("/") not in PATHS:
            await self.app(scope, receive, send)
            return
        oversized = JSONResponse({"detail": "AI request is too large."}, status_code=413)
        content_length = dict(scope.get("headers", [])).get(b"content-length")
        if content_length is not None:
            try:
                length = int(content_length)
            except ValueError:
                await JSONResponse({"detail": "Invalid AI request."}, status_code=422)(scope, receive, send)
                return
            if length < 0 or length > MAX_REQUEST_BYTES:
                await oversized(scope, receive, send)
                return
        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            chunk = message.get("body", b"")
            if len(body) + len(chunk) > MAX_REQUEST_BYTES:
                await oversized(scope, receive, send)
                return
            body.extend(chunk)
            if not message.get("more_body", False):
                break
        consumed = False

        async def bounded_receive():
            nonlocal consumed
            if not consumed:
                consumed = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()

        await self.app(scope, bounded_receive, send)
