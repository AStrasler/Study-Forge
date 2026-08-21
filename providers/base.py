"""
Common provider interface.

All local and cloud providers implement this contract so the pipeline
never depends on a concrete provider.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


class ProviderError(Exception):
    """Raised when a provider fails in a way that should trigger fallback."""

    def __init__(self, message: str, *, provider: str, retriable: bool = False):
        super().__init__(message)
        self.provider = provider
        self.retriable = retriable


@dataclass
class ProviderResponse:
    text: str
    provider: str
    model: str
    raw: Optional[Dict[str, Any]] = None


class BaseProvider(ABC):
    """Minimal interface every provider must satisfy."""

    name: str  # short identifier used in config / fallback lists

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the provider appears reachable and configured."""
        ...

    @abstractmethod
    def generate(self, prompt: str, *, system: Optional[str] = None, **kwargs: Any) -> ProviderResponse:
        """
        Generate a completion.

        Must raise ProviderError on authentication, connection, timeout,
        empty/invalid response, or provider-specific API errors so the
        manager can fall back.
        """
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"
