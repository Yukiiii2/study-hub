"""Private Storage API only. Current secret keys are apikeys, never bearer JWTs."""
from contextlib import contextmanager
from urllib.parse import quote, urlencode, urlsplit

import httpx

from app.core.config import get_settings
from app.services.resource_errors import MAX_FILE_BYTES, ResourceError

BUCKET = "study-resources"
UNAVAILABLE = "File storage is unavailable. Try again."


class ResourceStorage:
    def __init__(self, *, settings=None, client=None):
        self.settings = settings or get_settings()
        self.client = client

    def _configuration(self):
        key = self.settings.supabase_secret_key.get_secret_value()
        base = self.settings.supabase_url.rstrip("/")
        if not base or not key:
            raise ResourceError(503, UNAVAILABLE)
        return base + "/storage/v1", {"apikey": key}

    @contextmanager
    def _client(self):
        if self.client is not None:
            yield self.client
        else:
            with httpx.Client(timeout=20.0, follow_redirects=False) as client:
                yield client

    def _request(self, method, endpoint, **kwargs):
        base, headers = self._configuration()
        headers.update(kwargs.pop("headers", {}))
        try:
            with self._client() as client:
                return client.request(method, base + endpoint, headers=headers, **kwargs)
        except (httpx.HTTPError, httpx.InvalidURL):
            raise ResourceError(503, UNAVAILABLE) from None

    @staticmethod
    def _object(path):
        return f"/{BUCKET}/{quote(path, safe='/')}"

    def ensure_bucket(self):
        """Explicit setup operation; never called on application startup or upload."""
        response = self._request("GET", f"/bucket/{BUCKET}")
        if self._missing(response):
            created = self._request("POST", "/bucket", json={"id": BUCKET, "name": BUCKET, "public": False,
                "file_size_limit": MAX_FILE_BYTES, "allowed_mime_types": ["application/pdf", "text/csv"]})
            if created.status_code not in (200, 201, 409):
                raise ResourceError(503, UNAVAILABLE)
            response = self._request("GET", f"/bucket/{BUCKET}")
        if response.status_code != 200:
            raise ResourceError(503, UNAVAILABLE)
        try:
            bucket = response.json()
            if bucket.get("id") != BUCKET or bucket.get("public") is not False:
                raise ResourceError(503, "Resource storage must use a private study-resources bucket.")
            if bucket.get("file_size_limit") != MAX_FILE_BYTES or set(bucket.get("allowed_mime_types") or []) != {"application/pdf", "text/csv"}:
                raise ResourceError(503, "Resource storage requires a 4 MiB limit and PDF/CSV MIME restrictions.")
        except (ValueError, AttributeError):
            raise ResourceError(503, UNAVAILABLE) from None
        return {"id": BUCKET, "public": False}

    @staticmethod
    def _missing(response):
        if response.status_code == 404:
            return True
        if response.status_code == 400:
            try:
                payload = response.json()
                return str(payload.get("statusCode")) == "404" or payload.get("error") == "not_found"
            except (ValueError, AttributeError):
                pass
        return False

    def upload(self, path, data, mime):
        response = self._request("POST", "/object" + self._object(path), content=data,
                                 headers={"Content-Type": mime, "x-upsert": "false"})
        if response.status_code not in (200, 201):
            raise ResourceError(503, UNAVAILABLE)

    def delete(self, path):
        response = self._request("DELETE", f"/object/{BUCKET}", json={"prefixes": [path]})
        if response.status_code in (200, 204) or self._missing(response):
            return
        raise ResourceError(503, UNAVAILABLE)

    def sign(self, path, *, download=True):
        response = self._request("POST", "/object/sign" + self._object(path), json={"expiresIn": 120})
        if response.status_code != 200:
            raise ResourceError(503, UNAVAILABLE)
        try:
            signed = response.json()["signedURL"]
            if not isinstance(signed, str) or not signed.startswith("/object/sign/"):
                raise ValueError()
            base, _ = self._configuration()
            url = base + signed
            if download:
                url += ("&" if urlsplit(url).query else "?") + urlencode({"download": path.rsplit("/", 1)[-1]})
            return url
        except (ValueError, KeyError, TypeError):
            raise ResourceError(503, UNAVAILABLE) from None

    def read(self, path):
        base, headers = self._configuration()
        try:
            with self._client() as client:
                with client.stream("GET", base + "/object" + self._object(path), headers=headers) as response:
                    if response.status_code != 200:
                        raise ResourceError(503, UNAVAILABLE)
                    chunks = []
                    size = 0
                    for chunk in response.iter_bytes(chunk_size=65536):
                        size += len(chunk)
                        if size > MAX_FILE_BYTES:
                            raise ResourceError(503, UNAVAILABLE)
                        chunks.append(chunk)
                    return b"".join(chunks)
        except (httpx.HTTPError, httpx.InvalidURL):
            raise ResourceError(503, UNAVAILABLE) from None


def main():
    import sys
    try:
        ResourceStorage().ensure_bucket()
    except (ResourceError, ValueError):
        print("Private resource storage setup failed. Check backend configuration and bucket access.", file=sys.stderr)
        return 1
    print("Private study-resources bucket verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
