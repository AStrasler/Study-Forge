"""
Ollama local provider.

Talks to a running Ollama instance over its HTTP API.
No API key required.
"""

from __future__ import annotations

from typing import Any, Optional

import httpx

from .base import BaseProvider, ProviderError, ProviderResponse


class OllamaProvider(BaseProvider):
    name = "ollama"

    def __init__(self, model: str, base_url: str = "http://localhost:11434", timeout: int = 120):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def is_available(self) -> bool:
        try:
            with httpx.Client(timeout=5.0) as client:
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

        # Allow caller to pass extra Ollama options if needed
        if "options" in kwargs:
            payload["options"] = kwargs["options"]

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(f"{self.base_url}/api/generate", json=payload)
        except httpx.TimeoutException as exc:
            raise ProviderError(
                f"Ollama request timed out after {self.timeout}s", provider=self.name, retriable=True
            ) from exc
        except httpx.RequestError as exc:
            raise ProviderError(
                f"Ollama connection failed: {exc}", provider=self.name, retriable=True
            ) from exc

        if resp.status_code != 200:
            raise ProviderError(
                f"Ollama returned HTTP {resp.status_code}: {resp.text[:300]}",
                provider=self.name,
            )

        try:
            data = resp.json()
        except Exception as exc:
            raise ProviderError("Ollama returned non-JSON response", provider=self.name) from exc

        text = (data.get("response") or "").strip()
        if not text:
            raise ProviderError("Ollama returned empty response", provider=self.name)

        return ProviderResponse(text=text, provider=self.name, model=self.model, raw=data)
