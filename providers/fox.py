"""
Fox provider implementation.

Fox is a high-performance local inference engine that acts as a
drop-in replacement for Ollama with continuous batching and faster
inference. It uses the same API interface as Ollama.

Docs: https://fox-gpt.com
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

import httpx

from providers.base import BaseProvider, ProviderResponse, ProviderError
from utils.logging import get_logger

logger = get_logger(__name__)


class FoxProvider(BaseProvider):
    """Fox local inference provider."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Fox provider.

        Args:
            config: Configuration dict with keys:
                - fox_base_url: str (default: http://localhost:8080)
                - fox_model: str (default: llama3.2:3b)
                - fox_timeout: int (default: 300)
        """
        self.base_url = config.get("fox_base_url", "http://localhost:8080")
        self.model = config.get("fox_model", "llama3.2:3b")
        self.timeout = config.get("fox_timeout", 300)
        self._available = None
        self._client = httpx.Client(timeout=self.timeout)

    def is_available(self) -> bool:
        """Check if Fox is available and the model is loaded."""
        if self._available is not None:
            return self._available

        try:
            # Fox uses the same /api/tags endpoint as Ollama
            response = self._client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                if self.model in models:
                    self._available = True
                    logger.info("Fox available with model: %s", self.model)
                else:
                    logger.warning(
                        "Fox model %s not found. Available: %s",
                        self.model,
                        ", ".join(models) or "none",
                    )
                    self._available = False
            else:
                logger.warning("Fox unavailable (status %s)", response.status_code)
                self._available = False
        except Exception as e:
            logger.warning("Fox unavailable: %s", e)
            self._available = False

        return self._available

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> ProviderResponse:
        """
        Generate a response using Fox.

        Args:
            prompt: The user prompt.
            system_prompt: Optional system prompt.
            **kwargs: Additional generation parameters.

        Returns:
            ProviderResponse containing the generated text.

        Raises:
            ProviderError: If generation fails.
        """
        if not self.is_available():
            raise ProviderError("Fox is not available")

        try:
            # Fox uses the same /api/generate endpoint as Ollama
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.9),
                },
            }

            if system_prompt:
                payload["system"] = system_prompt

            response = self._client.post(
                f"{self.base_url}/api/generate",
                json=payload,
            )

            if response.status_code != 200:
                raise ProviderError(
                    f"Fox generation failed (status {response.status_code}): {response.text}"
                )

            data = response.json()
            if "response" not in data:
                raise ProviderError("Fox response missing 'response' field")

            return ProviderResponse(
                text=data["response"].strip(),
                model=self.model,
                provider="fox",
                raw_response=data,
            )

        except httpx.TimeoutException:
            raise ProviderError("Fox generation timed out")
        except json.JSONDecodeError as e:
            raise ProviderError(f"Fox returned malformed JSON: {e}")
        except Exception as e:
            raise ProviderError(f"Fox generation failed: {e}")

    def get_config(self) -> Dict[str, Any]:
        """Return provider configuration."""
        return {
            "provider": "fox",
            "base_url": self.base_url,
            "model": self.model,
            "timeout": self.timeout,
        }

    def __repr__(self) -> str:
        return f"FoxProvider(base_url={self.base_url}, model={self.model})"