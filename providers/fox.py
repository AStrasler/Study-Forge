"""
Fox local provider (optional).

Fox is an Ollama-compatible local inference server (default port 8080).
If Fox is not installed or not running, is_available() returns False and
the manager skips it — no setup required for users who only use Ollama.

Ref: https://github.com/ferrumox/fox
"""

from __future__ import annotations

from typing import Any, Optional

import httpx

from .base import BaseProvider, ProviderError, ProviderResponse


class FoxProvider(BaseProvider):
    name = "fox"

    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str = "http://localhost:8080",
        timeout: int = 300,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def is_available(self) -> bool:
        try:
            with httpx.Client(timeout=3.0) as client:
                resp = client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    def generate(self, prompt: str, *, system: Optional[str] = None, **kwargs: Any) -> ProviderResponse:
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        if system:
            payload["system"] = system

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(f"{self.base_url}/api/generate", json=payload)
        except httpx.TimeoutException as exc:
            raise ProviderError(
                f"Fox request timed out after {self.timeout}s",
                provider=self.name,
                retriable=True,
            ) from exc
        except httpx.RequestError as exc:
            raise ProviderError(
                f"Fox connection failed: {exc}",
                provider=self.name,
                retriable=True,
            ) from exc

        if resp.status_code != 200:
            raise ProviderError(
                f"Fox returned HTTP {resp.status_code}: {resp.text[:200]}",
                provider=self.name,
            )

        try:
            data = resp.json()
        except Exception as exc:
            raise ProviderError("Fox returned non-JSON response", provider=self.name) from exc

        text = (data.get("response") or "").strip()
        if not text:
            raise ProviderError("Fox returned empty response", provider=self.name)

        return ProviderResponse(text=text, provider=self.name, model=self.model, raw=data)
