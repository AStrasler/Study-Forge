"""Definitions agent — identifies important terminology and explains it."""

from __future__ import annotations

from providers.base import ProviderResponse
from providers.manager import ProviderManager

SYSTEM = (
    "You identify important terms and provide clear, accurate definitions "
    "based only on the provided study material. "
    "Do not invent definitions that are not supported by the text."
)


def run(text: str, manager: ProviderManager) -> ProviderResponse:
    prompt = (
        "Extract key terms and their definitions from the following study material.\n"
        "Format as:\nTerm: definition\n\n"
        f"Material:\n{text}"
    )
    return manager.generate(prompt, system=SYSTEM)
