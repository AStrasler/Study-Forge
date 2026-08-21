"""Summarizer agent — produces a concise lecture summary."""

from __future__ import annotations

from providers.base import ProviderResponse
from providers.manager import ProviderManager

SYSTEM = (
    "You are a precise academic summarizer. "
    "Produce a clear, concise summary of the lecture or study material. "
    "Focus on the main ideas and structure. Do not invent information."
)


def run(text: str, manager: ProviderManager) -> ProviderResponse:
    prompt = f"Summarize the following study material:\n\n{text}"
    return manager.generate(prompt, system=SYSTEM)
