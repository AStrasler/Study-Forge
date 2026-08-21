"""
Provider manager — selects providers according to fallback order and
handles real failures (not subjective quality).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from config.settings import Settings
from utils.logging import get_logger

from .base import BaseProvider, ProviderError, ProviderResponse
from .groq import GroqProvider
from .ollama import OllamaProvider

logger = get_logger(__name__)


class ProviderManager:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._providers: Dict[str, BaseProvider] = {}
        self._build_providers()

    def _build_providers(self) -> None:
        # Local
        if self.settings.local_provider == "ollama":
            self._providers["ollama"] = OllamaProvider(
                model=self.settings.local_model,
                base_url=self.settings.ollama_base_url,
                timeout=self.settings.provider_timeout,
            )
        # Future: fox, mullama

        # Cloud — only register when credentials exist
        if self.settings.groq_api_key:
            self._providers["groq"] = GroqProvider(
                api_key=self.settings.groq_api_key,
                model=self.settings.groq_model,
                timeout=min(self.settings.provider_timeout, 120),
            )

        # Future: cloudflare, gemini, huggingface

    def get_ordered_providers(self) -> List[BaseProvider]:
        ordered: List[BaseProvider] = []
        for name in self.settings.provider_fallback_order:
            provider = self._providers.get(name)
            if provider is not None:
                ordered.append(provider)
        return ordered

    def generate(self, prompt: str, *, system: Optional[str] = None, **kwargs: Any) -> ProviderResponse:
        """
        Try providers in configured order until one succeeds.
        Only real provider failures trigger the next fallback.
        """
        last_error: Optional[Exception] = None
        ordered = self.get_ordered_providers()

        if not ordered:
            raise ProviderError(
                "No providers configured. Set LOCAL_PROVIDER/Ollama or a cloud API key.",
                provider="manager",
            )

        for provider in ordered:
            if not provider.is_available():
                logger.warning("Provider %s is not available — skipping", provider.name)
                continue

            try:
                logger.info("Trying provider: %s", provider.name)
                response = provider.generate(prompt, system=system, **kwargs)
                logger.info("Provider %s succeeded", provider.name)
                return response
            except ProviderError as exc:
                logger.warning("Provider %s failed: %s", provider.name, exc)
                last_error = exc
                continue
            except Exception as exc:
                logger.warning("Provider %s raised unexpected error: %s", provider.name, exc)
                last_error = exc
                continue

        raise ProviderError(
            f"All configured providers failed. Last error: {last_error}",
            provider="manager",
        )
