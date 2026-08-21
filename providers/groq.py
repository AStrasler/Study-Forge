"""
Groq cloud provider (BYOK).

Uses the OpenAI-compatible Chat Completions API at:
  https://api.groq.com/openai/v1/chat/completions

Requires GROQ_API_KEY. Never logs the key.
"""

from __future__ import annotations

from typing import Any, Optional

import httpx

from .base import BaseProvider, ProviderError, ProviderResponse

DEFAULT_MODEL = "openai/gpt-oss-20b"
BASE_URL = "https://api.groq.com/openai/v1"


class GroqProvider(BaseProvider):
    name = "groq"

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL, timeout: int = 120):
        self.api_key = (api_key or "").strip()
        self.model = model or DEFAULT_MODEL
        self.timeout = timeout

    def is_available(self) -> bool:
        if not self.api_key:
            return False
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(
                    f"{BASE_URL}/models",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                )
                return resp.status_code == 200
        except Exception:
            return False

    def generate(self, prompt: str, *, system: Optional[str] = None, **kwargs: Any) -> ProviderResponse:
        if not self.api_key:
            raise ProviderError("Groq API key not configured", provider=self.name)

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
        }
        if "max_tokens" in kwargs:
            payload["max_tokens"] = kwargs["max_tokens"]

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(
                    f"{BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload,
                )
        except httpx.TimeoutException as exc:
            raise ProviderError(
                f"Groq request timed out after {self.timeout}s",
                provider=self.name,
                retriable=True,
            ) from exc
        except httpx.RequestError as exc:
            raise ProviderError(
                f"Groq connection failed: {exc}",
                provider=self.name,
                retriable=True,
            ) from exc

        if resp.status_code == 401:
            raise ProviderError("Groq authentication failed (check GROQ_API_KEY)", provider=self.name)
        if resp.status_code == 429:
            raise ProviderError("Groq rate limit exceeded", provider=self.name, retriable=True)
        if resp.status_code != 200:
            # Do not include full body if it might echo secrets; truncate safely
            raise ProviderError(
                f"Groq returned HTTP {resp.status_code}: {resp.text[:200]}",
                provider=self.name,
            )

        try:
            data = resp.json()
        except Exception as exc:
            raise ProviderError("Groq returned non-JSON response", provider=self.name) from exc

        try:
            text = (data["choices"][0]["message"]["content"] or "").strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError("Groq response missing choices/message/content", provider=self.name) from exc

        if not text:
            raise ProviderError("Groq returned empty response", provider=self.name)

        return ProviderResponse(text=text, provider=self.name, model=self.model, raw=data)
