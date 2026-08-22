"""
Mullama local provider (optional).

Uses Mullama's Ollama-compatible HTTP server when running.
Default base URL: http://localhost:11435 (so it does not collide with Ollama on 11434).

If Mullama is not installed or not serving, is_available() returns False and
the manager skips it — no setup required for users who only use Ollama.

Ref: https://github.com/neul-labs/mullama
"""

from __future__ import annotations

from typing import Any, Optional

import httpx

from .base import BaseProvider, ProviderError, ProviderResponse


class MullamaProvider(BaseProvider):
    name = "mullama"

    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str = "http://localhost:11435",
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
                f"Mullama request timed out after {self.timeout}s",
                provider=self.name,
                retriable=True,
            ) from exc
        except httpx.RequestError as exc:
            raise ProviderError(
                f"Mullama connection failed: {exc}",
                provider=self.name,
                retriable=True,
            ) from exc

        if resp.status_code != 200:
            raise ProviderError(
                f"Mullama returned HTTP {resp.status_code}: {resp.text[:200]}",
                provider=self.name,
            )

        try:
            data = resp.json()
        except Exception as exc:
            raise ProviderError("Mullama returned non-JSON response", provider=self.name) from exc

        text = (data.get("response") or "").strip()
        if not text:
            raise ProviderError("Mullama returned empty response", provider=self.name)

        return ProviderResponse(text=text, provider=self.name, model=self.model, raw=data)
