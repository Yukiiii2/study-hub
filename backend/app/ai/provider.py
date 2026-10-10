"""Gemini REST adapter. No SDK, redirects, retries, tools or content logging."""
import asyncio
import json
from typing import Protocol

import httpx

from app.ai.errors import AIError
from app.core.config import get_settings

MAX_RESPONSE_BYTES = 96 * 1024
MAX_OUTPUT_CHARS = 24000


class StudyProvider(Protocol):
    provider: str
    model: str

    async def generate(self, *, system: str, material: str, schema: dict) -> dict: ...


class GeminiProvider:
    provider = "gemini"

    def __init__(self, key, model, *, transport=None):
        self.key = key
        self.model = model
        self.transport = transport

    async def generate(self, *, system, material, schema):
        try:
            async with asyncio.timeout(30):
                async with httpx.AsyncClient(timeout=30, follow_redirects=False, transport=self.transport) as client:
                    async with client.stream(
                        "POST", f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent",
                        headers={"x-goog-api-key": self.key.get_secret_value()},
                        json={"systemInstruction": {"parts": [{"text": system}]},
                              "contents": [{"role": "user", "parts": [{"text": material}]}],
                              "generationConfig": {"responseMimeType": "application/json",
                                                   "responseJsonSchema": schema,
                                                   "maxOutputTokens": 4096, "candidateCount": 1}},
                    ) as response:
                        if response.status_code != 200:
                            raise AIError(503, "AI provider is unavailable. Try again.")
                        body = bytearray()
                        async for chunk in response.aiter_bytes():
                            if len(body) + len(chunk) > MAX_RESPONSE_BYTES:
                                raise AIError(502, "AI returned an invalid response. Try again.")
                            body.extend(chunk)
            payload = json.loads(body)
            candidates = payload.get("candidates", [])
            if len(candidates) != 1 or candidates[0].get("finishReason") != "STOP":
                raise ValueError("Incomplete response")
            parts = candidates[0]["content"]["parts"]
            if not parts or any(set(part) - {"text", "thought", "thoughtSignature"} for part in parts):
                raise ValueError("Unsupported response")
            output = "".join(part["text"] for part in parts if not part.get("thought"))
            if not output or len(output) > MAX_OUTPUT_CHARS:
                raise ValueError("Oversized output")
            return json.loads(output)
        except AIError:
            raise
        except (httpx.HTTPError, TimeoutError):
            raise AIError(503, "AI provider is unavailable. Try again.") from None
        except (ValueError, KeyError, TypeError, AttributeError, RecursionError):
            raise AIError(502, "AI returned an invalid response. Try again.") from None


def get_provider():
    # This function is injected as a lazy factory; context validation comes first.
    settings = get_settings()
    if not settings.gemini_api_key.get_secret_value() or not settings.gemini_model:
        raise AIError(503, "AI study assistance is not configured.")
    return GeminiProvider(settings.gemini_api_key, settings.gemini_model)
