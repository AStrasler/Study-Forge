"""
Provider manager — selects providers according to fallback order and
handles real failures (not subjective quality).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from config.settings import Settings
from utils.logging import get_logger

from .base import BaseProvider, ProviderError, ProviderResponse
from .fox import FoxProvider
from .groq import GroqProvider
from .lmstudio import LMStudioProvider
from .mullama import MullamaProvider
from .ollama import OllamaProvider

logger = get_logger(__name__)


class ProviderManager:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._providers: Dict[str, BaseProvider] = {}
        self._build_providers()

    def _build_providers(self) -> None:
        model = getattr(self.settings, "local_model", None) or self.settings.private_model

        self._providers["ollama"] = OllamaProvider(
            model=model,
            base_url=self.settings.ollama_base_url,
            timeout=self.settings.provider_timeout,
        )

        self._providers["lmstudio"] = LMStudioProvider(
            model=self.settings.lmstudio_model,
            base_url=self.settings.lmstudio_base_url,
            timeout=self.settings.provider_timeout,
        )

        self._providers["fox"] = FoxProvider(
            model=getattr(self.settings, "fox_model", model),
            base_url=getattr(self.settings, "fox_base_url", "http://localhost:8080"),
            timeout=int(getattr(self.settings, "fox_timeout", self.settings.provider_timeout)),
        )

        self._providers["mullama"] = MullamaProvider(
            model=getattr(self.settings, "mullama_model", model),
            base_url=getattr(self.settings, "mullama_base_url", "http://localhost:11435"),
            timeout=self.settings.provider_timeout,
        )

        if self.settings.groq_api_key:
            self._providers["groq"] = GroqProvider(
                api_key=self.settings.groq_api_key,
                model=self.settings.groq_model,
                timeout=min(self.settings.provider_timeout, 120),
            )

    def get_ordered_providers(self) -> List[BaseProvider]:
        ordered: List[BaseProvider] = []
        for name in self.settings.provider_fallback_order:
            provider = self._providers.get(name)
            if provider is not None:
                ordered.append(provider)
        # If order listed nothing registered, offer whatever we have
        if not ordered:
            ordered = list(self._providers.values())
        return ordered

    def generate(self, prompt: str, *, system: Optional[str] = None, **kwargs: Any) -> ProviderResponse:
        last_error: Optional[Exception] = None
        ordered = self.get_ordered_providers()

        if not ordered:
            raise ProviderError(
                "No providers configured. Set GROQ_API_KEY on Deepnote or a private provider.",
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
