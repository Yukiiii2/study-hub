"""Only safe, deliberate resource errors cross the HTTP boundary."""


class ResourceError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


MAX_FILE_BYTES = 4 * 1024 * 1024
MAX_REQUEST_BYTES = MAX_FILE_BYTES + 64 * 1024
