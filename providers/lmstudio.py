"""
LM Studio local provider.

Talks to a running LM Studio local server over its OpenAI-compatible
chat completions API. No API key required.
"""

from __future__ import annotations

from typing import Any, Optional

import httpx

from .base import BaseProvider, ProviderError, ProviderResponse


class LMStudioProvider(BaseProvider):
    name = "lmstudio"

    def __init__(self, model: str, base_url: str = "http://localhost:1234", timeout: int = 120):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def is_available(self) -> bool:
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(f"{self.base_url}/v1/models")
                return resp.status_code == 200
        except Exception:
            return False

    def generate(self, prompt: str, *, system: Optional[str] = None, **kwargs: Any) -> ProviderResponse:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }

        for key in ("temperature", "max_tokens", "top_p"):
            if key in kwargs:
                payload[key] = kwargs[key]

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(f"{self.base_url}/v1/chat/completions", json=payload)
        except httpx.TimeoutException as exc:
            raise ProviderError(
                f"LM Studio request timed out after {self.timeout}s", provider=self.name, retriable=True
            ) from exc
        except httpx.RequestError as exc:
            raise ProviderError(
                f"LM Studio connection failed: {exc}", provider=self.name, retriable=True
            ) from exc

        if resp.status_code != 200:
            raise ProviderError(
                f"LM Studio returned HTTP {resp.status_code}: {resp.text[:300]}",
                provider=self.name,
            )

        try:
            data = resp.json()
        except Exception as exc:
            raise ProviderError("LM Studio returned non-JSON response", provider=self.name) from exc

        try:
            text = (data["choices"][0]["message"]["content"] or "").strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError(
                f"LM Studio returned unexpected response shape: {data}", provider=self.name
            ) from exc

        if not text:
            raise ProviderError("LM Studio returned empty response", provider=self.name)

        return ProviderResponse(text=text, provider=self.name, model=self.model, raw=data)